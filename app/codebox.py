"""
Core Snekbox functionality, providing safe execution of Python code.

See config/snekbox.cfg for the default NsJail configuration.
"""

import os
import re
import shlex
import uuid
from pathlib import Path
from subprocess import TimeoutExpired, run
from tempfile import NamedTemporaryFile
from typing import Iterable, Optional

from loguru import logger

from . import config
from .models import Command, Response, Sourcefiles
from .utils import SandboxDirectory, inside_container, save_sources

assert inside_container()

# [level][timestamp][PID]? function_signature:line_no? message
LOG_PATTERN = re.compile(
    r'\[(?P<level>(I)|[DWEF])\]\[.+?\](?(2)|(?P<func>\[\d+\] .+?:\d+ )) ?(?P<msg>.+)'
)
LOG_BLACKLIST = ('Process will be ',)


def _parse_log(log_lines: Iterable[str]) -> None:
    """
    Parse and log NsJail's log messages.
    """
    for line in log_lines:
        match = LOG_PATTERN.fullmatch(line)
        if match is None:
            logger.warning(f"Failed to parse log line '{line}'")
            continue

        msg = match['msg']
        if not config.DEBUG and any(msg.startswith(s) for s in LOG_BLACKLIST):
            # Skip blacklisted messages if not debugging.
            continue

        if config.DEBUG and match['func']:
            # Prepend PID, function signature, and line number if debugging.
            msg = f"{match['func']}{msg}"

        if match['level'] == 'D':
            logger.debug(msg)
        elif match['level'] == 'I':
            if config.DEBUG or msg.startswith('pid='):
                # Skip messages unrelated to process exit if not debugging.
                logger.info(msg)
        elif match['level'] == 'W':
            logger.warning(msg)
        else:
            # Treat fatal as error.
            logger.error(msg)


class NSJail:
    def __init__(self, cwd: Optional[Path] = None) -> None:
        self.cwd = cwd or Path.cwd()
        self.cgroup_name = self.pid = self.mem = None

    def __enter__(self):
        """
        Create a PID and memory cgroup for NsJail to use as the parent cgroup.

        NsJail doesn't do this automatically because it requires privileges NsJail usually doesn't
        have.

        Disables memory swapping.
        """
        # Pick a name for the cgroup
        self.cgroup_name = 'codebox-' + str(uuid.uuid4())

        self.pids = config.CGROUP_PIDS_PATH / self.cgroup_name
        self.pids.mkdir(parents=True, exist_ok=True)
        self.mem = config.CGROUP_MEMORY_PATH / self.cgroup_name
        self.mem.mkdir(parents=True, exist_ok=True)
        mem_max = str(config.CGROUP_MEM_MAX)

        # Swap limit cannot be set to a value lower than memory.limit_in_bytes.
        # Therefore, this must be set before the swap limit.
        #
        # Since child cgroups are dynamically created, the swap limit has to be set on the parent
        # instead so that children inherit it. Given the swap's dependency on the memory limit,
        # the memory limit must also be set on the parent. NsJail only sets the memory limit for
        # child cgroups, not the parent.
        (self.mem / 'memory.limit_in_bytes').write_text(mem_max, encoding='utf-8')

        try:
            # Swap limit is specified as the sum of the memory and swap limits.
            # Therefore, setting it equal to the memory limit effectively disables swapping.
            (self.mem / 'memory.memsw.limit_in_bytes').write_text(mem_max, encoding='utf-8')
        except PermissionError:
            logger.warning(
                'Failed to set the memory swap limit for the cgroup. '
                'This is probably because CONFIG_MEMCG_SWAP or CONFIG_MEMCG_SWAP_ENABLED is unset. '
                'Please ensure swap memory is disabled on the system.'
            )
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.pids.rmdir()
            self.mem.rmdir()
        except OSError:
            logger.warning(f'Orphan cgroup: {self.cgroup_name}')

    def execute(self, command: Command) -> Response:
        """
        Execute a command in an isolated environment and return its response.
        """
        with NamedTemporaryFile() as nsj_log:
            # fmt: off
            args = (
                config.NSJAIL_PATH,
                '--config', config.NSJAIL_CFG,
                '--bindmount', f'{self.cwd}:/sandbox',
                '--log', nsj_log.name,
                '--cgroup_mem_parent', self.cgroup_name,
                '--cgroup_pids_parent', self.cgroup_name,
                '--cgroup_mem_max', str(config.CGROUP_MEM_MAX),
                '--cgroup_pids_max', str(config.CGROUP_PIDS_MAX),
                '--', *shlex.split(command.command),
            )
            # fmt: on
            exit_code = -1
            stdout = stderr = ''
            try:
                process = run(
                    args,  # type: ignore
                    input=command.stdin,
                    timeout=command.timeout,
                    capture_output=True,
                    text=True,
                )
                logger.debug(process)
                stdout = process.stdout
                stderr = process.stderr
                exit_code = process.returncode
            except TimeoutExpired as error:
                stdout = error.stdout or ''
                stderr = error.stderr or f'Timeout Error. Exceeded {error.timeout}s'
            except Exception as error:
                stderr = str(error)

            if exit_code and not stderr:
                log_lines = nsj_log.read().decode('utf-8').splitlines()
                _parse_log(log_lines)

        return Response(stdout=stdout, stderr=stderr, exit_code=exit_code)


def run_project(sources: Sourcefiles, commands: list[Command]) -> list[Response]:
    responses = []
    with SandboxDirectory() as sandbox:
        os.chmod(sandbox, 0o0777)  # to be used in nsjail later
        logger.info(sources)
        save_sources(sandbox, sources)
        with NSJail() as nsjail:
            for command in commands:
                logger.info(command)
                resp = nsjail.execute(command)
                logger.info(resp)
                responses.append(resp)
    return responses
