import io
import json
from pathlib import Path

from pytest import mark

from .conftest import projects, run_inside_container

from app.codebox import execute, run_project, save_sources  # isort:skip
from app.main import main   # isort:skip
from app.models import Command, ProjectCore, Response  # isort:skip


TIMEOUT = 0.1

# Skip all test functions of a module
pytestmark = run_inside_container


def test_save_sources(tmp_path: Path) -> None:
    sources = {
        'a': 'aaaa',
        'b': 'bbb',
        'app/d': 'ddd',
        'app/x/e': 'eee',
        'images/f': 'fff',
        '/images/g': 'ggg',
    }
    save_sources(tmp_path, sources)
    assert len(list(tmp_path.glob('**/*'))) == 9


@mark.parametrize(
    'command,response',
    [
        (
            Command(command='echo 1 2 3', timeout=TIMEOUT),
            Response(stdout='1 2 3\n', stderr='', exit_code=0),
        ),
        (
            Command(command='python -c "print(1, 2, 3)"', timeout=TIMEOUT),
            Response(stdout='1 2 3\n', stderr='', exit_code=0),
        ),
        (
            Command(command=f'sleep {TIMEOUT + 0.05}', timeout=TIMEOUT),
            Response(stdout='', stderr=f'Timeout Error. Exceeded {TIMEOUT}s', exit_code=-1),
        ),
        (Command(command='', timeout=TIMEOUT), Response(stdout='', stderr='', exit_code=0)),
        (
            Command(command='nao_existe 1 2 3', timeout=TIMEOUT),
            Response(stdout='', stderr='/bin/sh: 1: nao_existe: not found\n', exit_code=127),
        ),
        (
            Command(command='rm -rf /tmp/try-to-remove.me', timeout=TIMEOUT),  # file created in Dockerfile.test
            Response(
                stdout='', stderr="rm: cannot remove '/tmp/try-to-remove.me': Operation not permitted\n", exit_code=1
            ),
        ),
    ],
)
def test_execute(command, response):
    result = execute(command)
    assert response == result


@mark.parametrize('sources,commands,responses', projects)
def test_run_project(sources, commands, responses):
    assert run_project(sources, commands) == responses


def test_main(capsys, monkeypatch):
    sources = projects[-1][0]
    commands = projects[-1][1][:2]
    responses = projects[-1][2][:2]
    project = ProjectCore(sources=sources, commands=commands).json()
    monkeypatch.setattr('sys.stdin', io.StringIO(project))
    main()
    stdout = json.loads(capsys.readouterr().out)
    output = [Response(**resp) for resp in stdout]
    assert responses == output
