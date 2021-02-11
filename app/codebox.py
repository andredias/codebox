import json
import os
import sys
from pathlib import Path
from subprocess import TimeoutExpired, run

from .models import Command, CodeboxInput, Response, Sourcefiles
from .utils import SandboxDirectory


def save_sources(dest_dir: Path, sources: Sourcefiles) -> None:
    '''
    Save sources to a temporary directory
    '''
    for path, code in sources.items():
        p = dest_dir / path.lstrip(os.sep)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(code)
    return


def run_project(sources: Sourcefiles, commands: list[Command]) -> list[Response]:
    responses = []
    with SandboxDirectory() as sandbox:
        save_sources(sandbox, sources)
        for command in commands:
            resp = execute(command)
            responses.append(resp)
    return responses


def execute(command: Command) -> Response:
    exit_code = -1
    stdout = stderr = ''
    try:
        process = run(
            command.command,
            input=command.input,
            timeout=command.timeout,
            shell=True,
            capture_output=True,
            text=True
        )
        stdout = process.stdout
        stderr = process.stderr
        exit_code = process.returncode
    except TimeoutExpired as error:
        stdout = error.stdout or ''
        stderr = error.stderr or f'Timeout Error. Exceeded {error.timeout}s'
    except Exception as error:
        stderr = str(error)

    response = Response(
        stdout=stdout,
        stderr=stderr,
        exit_code=exit_code,
    )
    return response
