"""
Core Snekbox functionality, providing safe execution of Python code.

See config/snekbox.cfg for the default NsJail configuration.
"""

import os
import re
import shlex
from pathlib import Path
from subprocess import TimeoutExpired, run
from tempfile import NamedTemporaryFile
from time import perf_counter
from typing import Iterable

from loguru import logger

from . import config
from .models import Command, Response, Sourcefiles
from .utils import SandboxDirectory, inside_container, save_source

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


def execute(command: Command) -> Response:
    """
    Execute a command in an isolated environment and return its response.
    """
    with NamedTemporaryFile() as nsj_log:
        # fmt: off
        arguments = (
            config.NSJAIL_PATH,
            '--config', config.NSJAIL_CFG,
            '--bindmount', f'{Path.cwd()}:/sandbox',
            '--log', nsj_log.name,
            '--', *shlex.split(command.command)
        )
        # fmt: on
        exit_code = -1
        stdout = stderr = ''
        try:
            process = run(
                arguments,  # type: ignore
                input=command.stdin,
                timeout=command.timeout,
                capture_output=True,
                text=True,
            )
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
        for filepath, contents in sources.items():
            try:
                save_source(sandbox, filepath, contents)
            except Exception as error:
                logger.info(error)
                responses.append(Response(stderr=str(error), exit_code=-1))
        if responses:
            return responses
        for command in commands:
            logger.info(command)
            start_time = perf_counter()
            resp = execute(command)
            time = perf_counter() - start_time
            logger.info(f'Executed in {time * 1000:.2f}ms')
            logger.info(resp)
            responses.append(resp)
    return responses
