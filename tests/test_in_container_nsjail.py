from pytest import mark

from .conftest import run_inside_container

from app import config  # isort:skip
from app.models import Command, Response  # isort:skip
from app.nsjail import run_project  # isort:skip


TIMEOUT = 0.1

# Skip all test functions of a module
pytestmark = run_inside_container


projects = [
    (
        # 'empty project',
        {},
        [],
        [],
    ),
    (
        # 'only source, no command',
        {'hello.py': 'print("Olá mundo!")\n'},
        [],
        [],
    ),
    (
        # 'no source, one command',
        {},
        [Command(command='/bin/echo 1 2 3')],
        [Response(stdout='1 2 3\n', stderr='', exit_code=0)],
    ),
    (
        # 'multiple source files and commands',
        {  # sources
            'main.py': 'print("Olá mundo!")\n',
            'hello/hello.py': '''import sys

for line in sys.stdin.readlines():
    sys.stdout.write(line)
''',
        },
        [  # commands
            Command(command=f'/bin/sleep {TIMEOUT + 0.1}', timeout=TIMEOUT),
            Command(command='/usr/local/bin/python main.py'),
            Command(command='/usr/local/bin/python hello/hello.py', stdin='Olá\nAçúcar'),
            Command(command='/bin/cat hello.py'),
            Command(command='/bin/cat main.py'),
        ],
        [
            Response(stdout='', stderr=f'Timeout Error. Exceeded {TIMEOUT}s', exit_code=-1),
            Response(stdout='Olá mundo!\n', stderr='', exit_code=0),
            Response(stdout='Olá\nAçúcar', stderr='', exit_code=0),
            Response(
                stdout='', stderr='/bin/cat: hello.py: No such file or directory\n', exit_code=1
            ),
            Response(stdout='print("Olá mundo!")\n', stderr='', exit_code=0),
        ],
    ),
    (
        # 'time out error',
        {
            'hello.py': '''import sys

for line in sys.stdin.readlines():
    sys.stdout.write(line)
''',
        },
        [Command(command='/usr/local/bin/python hello.py', timeout=TIMEOUT)],
        [Response(stdout='', stderr=f'Timeout Error. Exceeded {TIMEOUT}s', exit_code=-1)],
    ),
]


@mark.parametrize('sources,commands,responses', projects)
def test_run_project(sources, commands, responses):
    assert run_project(sources, commands) == responses


def run_python(code) -> Response:
    command = Command(command='/usr/local/bin/python test.py')
    return run_project({'test.py': code}, [command])[0]


def test_while_true():
    code = 'while True:\n    pass'
    assert run_python(code) == Response(
        stdout='', stderr=f'Timeout Error. Exceeded {TIMEOUT}s', exit_code=-1
    )


def test_max_mem_test():
    code = f"x = ' ' * {config.CGROUP_MEM_MAX + 1_000}"
    assert run_python(code) == Response(stdout='', stderr='', exit_code=137)


def test_kill_process():
    code = '''import subprocess
print(subprocess.check_output('kill -9 6', shell=True).decode())
'''
    resp = run_python(code)
    assert 'BlockingIOError: [Errno 11] Resource temporarily unavailable' in resp.stderr
    assert resp.exit_code != 0


def test_write_file_to_sandbox_and_tmp():
    code = '''from pathlib import Path

Path('/sandbox/blabla.txt').write_text('bla bla bla')
Path('/tmp/blabla.txt').write_text('bla bla bla')
'''
    assert run_python(code) == Response(stdout='', stderr='', exit_code=0)


def test_write_in_protected_dirs():
    code = '''from pathlib import Path

count = 0
for path in ['/', '/bin', '/etc', '/lib', '/lib64', '/usr']:
    try:
        Path(path, 'test.txt').write_text('test')
    except OSError:
        count += 1

print(count)
'''
    assert run_python(code).stdout == '6\n'


def test_forkbomb_recode_unavailable():
    code = '''import os
while 1:
    os.fork()
    '''
    resp = run_python(code)
    assert 'BlockingIOError: [Errno 11] Resource temporarily unavailable' in resp.stderr
    assert resp.exit_code != 0


def test_multiprocessing_shared_memory_disabled():
    code = '''
from multiprocessing.shared_memory import SharedMemory
try:
    SharedMemory('test', create=True, size=16)
except FileExistsError:
    pass
'''
    resp = run_python(code)
    assert 'OSError: [Errno 38] Function not implemented' in resp.stderr
    assert resp.exit_code != 0
