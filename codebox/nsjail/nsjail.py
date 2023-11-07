import re
from collections.abc import Iterable
from functools import cache

from loguru import logger

from ..config import CGROUP_MEM_MAX, CGROUP_MEM_SWAP_MAX, CGROUP_PIDS_MAX, DEBUG
from . import cgroup, swap

# [level][timestamp][PID]? function_signature:line_no? message
LOG_PATTERN = re.compile(
    r'\[(?P<level>(I)|[DWEF])\]\[.+?\](?(2)|(?P<func>\[\d+\] .+?:\d+ )) ?(?P<msg>.+)'
)
LOG_BLACKLIST = ('Process will be ',)


def init() -> tuple[int, bool]:
    cgroup_version = cgroup.init()
    ignore_swap_limits = swap.should_ignore_limit(cgroup_version)

    logger.info(f'Assuming cgroup version {cgroup_version}.')
    return cgroup_version, ignore_swap_limits


def parse_log(log_lines: Iterable[str]) -> None:
    """
    Parse and log NsJail's log messages.
    """
    for line in log_lines:
        match = LOG_PATTERN.fullmatch(line)
        if match is None:
            logger.warning(f"Failed to parse log line '{line}'")
            continue

        msg = match['msg']
        if not DEBUG and any(msg.startswith(s) for s in LOG_BLACKLIST):
            # Skip blacklisted messages if not debugging.
            continue

        if DEBUG and match['func']:
            # Prepend PID, function signature, and line number if debugging.
            msg = f"{match['func']}{msg}"

        if match['level'] == 'D':
            logger.debug(msg)
        elif match['level'] == 'I':
            if DEBUG or msg.startswith('pid='):
                # Skip messages unrelated to process exit if not debugging.
                logger.info(msg)
        elif match['level'] == 'W':
            logger.warning(msg)
        else:
            # Treat fatal as error.
            logger.error(msg)


@cache
def get_nsjail_args() -> list[str]:
    cgroup_version, ignore_swap_limits = init()
    # fmt: off
    nsjail_args = [
        '--cgroup_mem_max', str(CGROUP_MEM_MAX),
        '--cgroup_pids_max', str(CGROUP_PIDS_MAX),
    ]
    if cgroup_version == 2:  # noqa: PLR2004
        nsjail_args.append('--use_cgroupv2')

    if ignore_swap_limits:
        nsjail_args.extend((
            '--cgroup_mem_memsw_max', '0',
            '--cgroup_mem_swap_max', '-1',
        ))
    else:
        nsjail_args.extend(('--cgroup_mem_swap_max', str(CGROUP_MEM_SWAP_MAX)))
    # fmt: on
    return nsjail_args
