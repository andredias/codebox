import re
import subprocess
import sys
import textwrap
from functools import cache
from subprocess import CompletedProcess
from tempfile import NamedTemporaryFile
from typing import Iterable

from loguru import logger

from ..config import (
    CGROUP_MEM_MAX,
    CGROUP_MEM_SWAP_MAX,
    CGROUP_PIDS_MAX,
    DEBUG,
    NSJAIL_CFG,
    NSJAIL_PATH,
)
from . import cgroup, swap

# [level][timestamp][PID]? function_signature:line_no? message
LOG_PATTERN = re.compile(
    r'\[(?P<level>(I)|[DWEF])\]\[.+?\](?(2)|(?P<func>\[\d+\] .+?:\d+ )) ?(?P<msg>.+)'
)
LOG_BLACKLIST = ('Process will be ',)

# Limit of stdout bytes we consume before terminating nsjail
OUTPUT_MAX = 1_000_000  # 1 MB
READ_CHUNK_SIZE = 10_000  # chars


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


def _consume_stdout(nsjail: subprocess.Popen) -> str:
    """
    Consume STDOUT, stopping when the output limit is reached or NsJail has exited.

    The aim of this function is to limit the size of the output received from
    NsJail to prevent container from claiming too much memory. If the output
    received from STDOUT goes over the OUTPUT_MAX limit, the NsJail subprocess
    is asked to terminate with a SIGKILL.

    Once the subprocess has exited, either naturally or because it was terminated,
    we return the output as a single string.
    """
    output_size = 0
    output = []

    # Context manager will wait for process to terminate and close file descriptors.
    with nsjail:
        # We'll consume STDOUT as long as the NsJail subprocess is running.
        while nsjail.poll() is None:
            chars = nsjail.stdout.read(READ_CHUNK_SIZE)  # type: ignore
            output_size += sys.getsizeof(chars)
            output.append(chars)

            if output_size > OUTPUT_MAX:
                # Terminate the NsJail subprocess with SIGTERM.
                # This in turn reaps and kills children with SIGKILL.
                logger.info('Output exceeded the output limit, sending SIGTERM to NsJail.')
                nsjail.terminate()
                break

    return ''.join(output)


@cache
def get_nsjail_args() -> list[str]:
    cgroup_version, ignore_swap_limits = init()
    # fmt: off
    nsjail_args = [
        '--cgroup_mem_max', str(CGROUP_MEM_MAX),
        '--cgroup_pids_max', str(CGROUP_PIDS_MAX),
    ]
    if cgroup_version == 2:
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


def python3(code: str, *, py_args: Iterable[str] = ('-c',)) -> CompletedProcess:
    """
    Execute Python 3 code in an isolated environment and return the completed process.

    The `nsjail_args` passed will be used to override the values in the NsJail config.
    These arguments are only options for NsJail; they do not affect Python's arguments.

    `py_args` are arguments to pass to the Python subprocess before the code,
    which is the last argument. By default, it's "-c", which executes the code given.
    """
    nsjail_args = get_nsjail_args()
    with NamedTemporaryFile() as nsj_log:
        args = (
            NSJAIL_PATH,
            '--config',
            NSJAIL_CFG,
            '--log',
            nsj_log.name,
            *nsjail_args,
            '--',
            '/venv/bin/python',
            *py_args,
            code,
        )

        msg = 'Executing code...'
        if DEBUG:
            msg = f"{msg[:-3]}:\n{textwrap.indent(code, '    ')}\nWith the arguments {args}."
        logger.info(msg)

        try:
            nsjail = subprocess.Popen(
                args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
        except ValueError:
            return CompletedProcess(args, -1, 'ValueError: embedded null byte', None)

        try:
            output = _consume_stdout(nsjail)
        except UnicodeDecodeError:
            return CompletedProcess(
                args,
                -1,
                'UnicodeDecodeError: invalid Unicode in output pipe',
                None,
            )

        # When you send signal `N` to a subprocess to terminate it using Popen, it
        # will return `-N` as its exit code. As we normally get `N + 128` back, we
        # convert negative exit codes to the `N + 128` form.
        returncode = -nsjail.returncode + 128 if nsjail.returncode < 0 else nsjail.returncode

        log_lines = nsj_log.read().decode('utf-8').splitlines()
        if not log_lines and returncode == 255:
            # NsJail probably failed to parse arguments so log output will still be in stdout
            log_lines = output.splitlines()

        parse_log(log_lines)

    logger.info(f'nsjail return code: {returncode}')

    return CompletedProcess(args, returncode, output, None)
