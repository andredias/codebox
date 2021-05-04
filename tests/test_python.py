from httpx import AsyncClient
from pydantic import parse_obj_as
from pytest import fixture, mark

from app.config import CGROUP_MEM_MAX, TIMEOUT
from app.models import Command, ProjectCore, Response


@fixture
def run_python(client: AsyncClient):
    async def _run_python(code: str) -> Response:
        sources = {'test.py': code}
        command = Command(command='/usr/local/bin/python test.py')
        resp = await client.post(
            '/execute', json=ProjectCore(sources=sources, commands=[command]).dict()
        )
        return Response(**(resp.json()[0]))

    return _run_python


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
]


@mark.parametrize('sources,commands,responses', projects)
async def test_run_project(client, sources, commands, responses):
    results = await client.post(
        '/execute', json=ProjectCore(sources=sources, commands=commands).dict()
    )
    assert results.status_code == 200
    assert parse_obj_as(list[Response], results.json()) == responses


async def test_while_true(run_python):
    code = 'while True:\n    pass'
    assert (await run_python(code)) == Response(
        stdout='', stderr=f'Timeout Error. Exceeded {TIMEOUT}s', exit_code=-1
    )


async def test_max_mem_test(run_python):
    code = f"x = ' ' * {CGROUP_MEM_MAX + 1_000}"
    assert (await run_python(code)) == Response(stdout='', stderr='', exit_code=137)


async def test_kill_process(run_python):
    code = '''import subprocess
print(subprocess.check_output('kill -9 6', shell=True).decode())
'''
    resp = await run_python(code)
    assert 'BlockingIOError: [Errno 11] Resource temporarily unavailable' in resp.stderr
    assert resp.exit_code != 0


async def test_write_file_to_sandbox_and_tmp(run_python):
    code = '''from pathlib import Path

Path('/sandbox/blabla.txt').write_text('bla bla bla')
Path('/tmp/blabla.txt').write_text('bla bla bla')
'''
    assert (await run_python(code)) == Response(stdout='', stderr='', exit_code=0)


async def test_write_in_protected_dirs(run_python):
    code = '''from pathlib import Path

count = 0
for path in ['/', '/bin', '/etc', '/lib', '/lib64', '/usr']:
    try:
        Path(path, 'test.txt').write_text('test')
    except OSError:
        count += 1

print(count)
'''
    assert (await run_python(code)).stdout == '6\n'


async def test_forkbomb_recode_unavailable(run_python):
    code = '''import os
while 1:
    os.fork()
    '''
    resp = await run_python(code)
    assert 'BlockingIOError: [Errno 11] Resource temporarily unavailable' in resp.stderr
    assert resp.exit_code != 0


async def test_multiprocessing_shared_memory_disabled(run_python):
    code = '''
from multiprocessing.shared_memory import SharedMemory
try:
    SharedMemory('test', create=True, size=16)
except FileExistsError:
    pass
'''
    resp = await run_python(code)
    assert 'OSError: [Errno 38] Function not implemented' in resp.stderr
    assert resp.exit_code != 0