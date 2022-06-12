"""
Core Snekbox functionality, providing safe execution of Python code.

See config/snekbox.cfg for the default NsJail configuration.
"""

import os
import shlex
from pathlib import Path
from subprocess import TimeoutExpired, run
from tempfile import NamedTemporaryFile
from time import perf_counter

from loguru import logger

from . import config
from .models import Command, Response, Sourcefiles
from .nsjail.nsjail import get_nsjail_args, parse_log
from .utils import SandboxDirectory, save_source


def execute(command: Command) -> Response:
    """
    Execute a command in an isolated environment and return its response.
    """
    nsjail_args = get_nsjail_args()
    start_time = perf_counter()
    with NamedTemporaryFile() as nsj_log:
        # fmt: off
        arguments = (
            config.NSJAIL_PATH,
            '--config', config.NSJAIL_CFG,
            '--env', 'HOME=/sandbox',
            '--cwd', '/sandbox',
            '--bindmount', f'{Path.cwd()}:/sandbox',
            '--log', nsj_log.name,
            *nsjail_args,
            '--', *shlex.split(command.command)
        )
        # fmt: on
        logger.debug(' '.join(arguments))
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
            parse_log(log_lines)

    elapsed_time = perf_counter() - start_time
    return Response(stdout=stdout, stderr=stderr, exit_code=exit_code, elapsed_time=elapsed_time)


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
            resp = execute(command)
            logger.info(resp)
            responses.append(resp)
    return responses
