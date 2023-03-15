"""
Core Snekbox functionality, providing safe execution of Python code.

See config/snekbox.cfg for the default NsJail configuration.
"""

import os
import shlex
from collections.abc import Callable, Sequence
from pathlib import Path
from subprocess import TimeoutExpired, run
from tempfile import NamedTemporaryFile, TemporaryDirectory
from time import perf_counter

from loguru import logger

from . import config
from .models import Command, Response, Sourcefiles
from .nsjail.nsjail import get_nsjail_args, parse_log
from .utils import save_source


def _execute(
    arguments: Sequence[str],
    stdin: str | None,
    timeout: float | None = config.TIMEOUT,
    cwd: str | Path | None = None,
) -> Response:
    """
    Execution core
    """
    logger.debug(' '.join(arguments))
    exit_code = -1
    stdout = stderr = ''
    start_time = perf_counter()
    try:
        process = run(
            arguments,  # type: ignore
            input=stdin,
            timeout=timeout,
            cwd=cwd,
            capture_output=True,
            text=True,
        )
        stdout = process.stdout
        stderr = process.stderr
        exit_code = process.returncode
    except TimeoutExpired as error:
        stdout = error.stdout and error.stdout.decode() or ''
        stderr = (
            error.stderr and error.stderr.decode() or f'Timeout Error. Exceeded {error.timeout}s'
        )
    except Exception as error:
        stderr = str(error)
    elapsed_time = perf_counter() - start_time
    return Response(stdout=stdout, stderr=stderr, exit_code=exit_code, elapsed_time=elapsed_time)


def execute(command: Command, sandbox_path: Path) -> Response:
    """
    Execute a command in an isolated environment and return its response.
    """
    nsjail_args = get_nsjail_args()
    with NamedTemporaryFile() as nsj_log:
        # fmt: off
        arguments = (
            config.NSJAIL_PATH,
            '--config', config.NSJAIL_CFG,
            '--env', 'HOME=/sandbox',
            '--cwd', '/sandbox',
            '--bindmount', f'{sandbox_path}:/sandbox',
            '--log', nsj_log.name,
            *nsjail_args,
            '--', *shlex.split(command.command)
        )
        # fmt: on
        response = _execute(arguments, command.stdin, command.timeout)
        if response.exit_code and not response.stderr:
            log_lines = nsj_log.read().decode('utf-8').splitlines()
            parse_log(log_lines)
    return response


def execute_insecure(command: Command, sandbox_path: Path) -> Response:
    """
    Execute a command directly in the container, without an isolated environment.
    It is interesting for running each command in a different container
    or to run the container in a different platform that doesn't run NsJail,
    such as linux/arm64 on MacOS
    """
    return _execute(
        (*shlex.split(command.command),),
        stdin=command.stdin,
        timeout=command.timeout,
        cwd=sandbox_path,
    )


def run_project(
    sources: Sourcefiles, commands: list[Command], exec_func: Callable = execute
) -> list[Response]:
    responses = []
    with TemporaryDirectory(prefix='sandbox_') as sandbox:
        sandbox_path = Path(sandbox)
        os.chmod(sandbox_path, 0o0777)  # to be used in nsjail later  # noqa: S103
        logger.info(sources)
        for filepath, contents in sources.items():
            try:
                save_source(sandbox_path, filepath, contents)
            except Exception as error:
                logger.info(error)
                responses.append(Response(stderr=str(error), exit_code=-1))
        if responses:
            return responses
        for command in commands:
            resp = exec_func(command, sandbox_path)
            logger.info(resp)
            responses.append(resp)
    return responses
