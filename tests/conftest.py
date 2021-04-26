import os
from pathlib import Path
from subprocess import run

from pytest import mark

from app.models import Command, Response

os.environ['TESTING'] = 'yes'


def inside_container() -> bool:
    """
    The developer's machine is not sandboxed and should not run any testing snippets, at the risk of being damaged.
    So, it is important to make sure that the code execution only happens inside a container.

    See:
    * https://stackoverflow.com/questions/23513045/how-to-check-if-a-process-is-running-inside-docker-container
    * https://stackoverflow.com/a/25518538/266362
    """
    return (
        Path('/.dockerenv').exists()
        or Path('/run/.containerenv').exists()
        or bool(run(['grep', ':/docker', '/proc/1/cgroup'], capture_output=True, text=True).stdout)
    )


run_inside_container = mark.skipif(not inside_container(), reason='not running inside a container')
run_outside_container = mark.skipif(inside_container(), reason='running inside a container')


TIMEOUT = 0.1


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
        [Command(command='echo 1 2 3')],
        [Response(stdout='1 2 3\n', stderr='', exit_code=0)],
    ),
    (  # multiple source files and commands
        {  # sources
            'main.py': 'print("Olá mundo!")\n',
            'hello/hello.py': '''import sys

for line in sys.stdin.readlines():
    sys.stdout.write(line)
''',
        },
        [  # commands
            Command(command=f'sleep {TIMEOUT + 0.1}', timeout=TIMEOUT),
            Command(command='python main.py'),
            Command(command='python hello/hello.py', stdin='Olá\nAçúcar'),
            Command(command='cat hello.py'),
            Command(command='cat main.py'),
        ],
        [
            Response(stdout='', stderr=f'Timeout Error. Exceeded {TIMEOUT}s', exit_code=-1),
            Response(stdout='Olá mundo!\n', stderr='', exit_code=0),
            Response(stdout='Olá\nAçúcar', stderr='', exit_code=0),
            Response(stdout='', stderr='cat: hello.py: No such file or directory\n', exit_code=1),
            Response(stdout='print("Olá mundo!")\n', stderr='', exit_code=0),
        ],
    ),
]
