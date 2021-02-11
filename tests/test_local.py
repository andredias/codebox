from pathlib import Path

from pytest import mark

from app.codebox import execute, run_project, save_sources  # isort:skip
from app.models import Command, Response  # isort:skip

TIMEOUT = 0.1


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


@mark.parametrize("command,response", [
    (
        Command(type='bash', command='echo 1 2 3', timeout=TIMEOUT),
        Response(stdout='1 2 3\n', stderr='', exit_code=0)
    ),
    (
        Command(type='bash', command='python -c "print(1, 2, 3)"', timeout=TIMEOUT),
        Response(stdout='1 2 3\n', stderr='', exit_code=0)
    ),
    (
        Command(type='bash', command=f'sleep {TIMEOUT + 0.05}', timeout=TIMEOUT),
        Response(stdout='', stderr=f'Timeout Error. Exceeded {TIMEOUT}s', exit_code=-1)
    ),
    (
        Command(type='bash', command='', timeout=TIMEOUT),
        Response(stdout='', stderr='', exit_code=0)
    ),
    (
        Command(type='bash', command='nao_existe 1 2 3', timeout=TIMEOUT),
        Response(stdout='', stderr='/bin/sh: 1: nao_existe: Permission denied\n', exit_code=127)
    ),
    (
        Command(type='bash', command='rm -rf /home', timeout=TIMEOUT),
        Response(stdout='', stderr="rm: cannot remove '/home': Permission denied\n", exit_code=1)
    )
])
def test_execute(command, response):
    result = execute(command)
    assert response == result


projects = [
    (  # empty project
        {},
        [],
        [],
    ),
    (  # only source, no command
        {'hello.py': 'print("Olá mundo!")\n'},
        [],
        [],
    ),
    (  # only command, no source
        {},
        [
            Command(command='echo 1 2 3'),
        ],
        [
            Response(stdout='1 2 3\n', stderr='', exit_code=0)
        ],
    ),
    (  # multiple source files and commands
        {  # sources
            'main.py': 'print("Olá mundo!")\n',
            'hello/hello.py': '''import sys

for line in sys.stdin.readlines():
    sys.stdout.write(line)
'''
        },
        [  # commands
            Command(command=f'sleep {TIMEOUT + 0.1}', timeout=TIMEOUT),
            Command(command='python main.py'),
            Command(command='python hello/hello.py', input='Olá\nAçúcar'),
            Command(command='python hello/hello.py', timeout=TIMEOUT),
            Command(command='cat hello.py'),
            Command(command='cat main.py'),
        ],
        [
            Response(stdout='', stderr=f'Timeout Error. Exceeded {TIMEOUT}s', exit_code=-1),
            Response(stdout='Olá mundo!\n', stderr='', exit_code=0),
            Response(stdout='Olá\nAçúcar', stderr='', exit_code=0),
            Response(stdout='', stderr=f'Timeout Error. Exceeded {TIMEOUT}s', exit_code=-1),
            Response(stdout='', stderr='cat: hello.py: No such file or directory\n', exit_code=1),
            Response(stdout='print("Olá mundo!")\n', stderr='', exit_code=0)
        ],
    ),
]


@mark.parametrize('sources,commands,responses', projects)
def test_run_project(sources, commands, responses):
    assert run_project(sources, commands) == responses
