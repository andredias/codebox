from flaky import flaky
from httpx import AsyncClient
from pydantic import TypeAdapter
from pytest import fixture, mark

from app.config import CGROUP_MEM_MAX, CGROUP_PIDS_MAX, TIMEOUT
from app.models import Command, ProjectCore, Response

list_response = TypeAdapter(list[Response])


@fixture
def run_python(client: AsyncClient):
    async def _run_python(code: str, timeout: float = 0.1) -> Response:
        sources = {'test.py': code}
        command = Command(command='/venv/bin/python test.py', timeout=timeout)
        resp = await client.post(
            '/execute', json=ProjectCore(sources=sources, commands=[command]).model_dump()
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
            'hello/hello.py': """import sys

for line in sys.stdin.readlines():
    sys.stdout.write(line)
""",
        },
        [  # commands
            Command(command=f'/bin/sleep {TIMEOUT + 0.1}', timeout=TIMEOUT),
            Command(command='/venv/bin/python main.py'),
            Command(command='/venv/bin/python hello/hello.py', stdin='Olá\nAçúcar'),
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
        {'invalid/path/../../../../usr/bin/help.py': 'test'},
        [],
        [Response(stderr='Invalid file path: /usr/bin/help.py', exit_code=-1)],
    ),
]


@mark.parametrize('sources,commands,responses', projects)
async def test_run_project(client, sources, commands, responses):
    results = await client.post(
        '/execute', json=ProjectCore(sources=sources, commands=commands).model_dump()
    )
    assert results.status_code == 200
    assert list_response.validate_python(results.json()) == responses


async def test_while_true(run_python):
    code = 'while True:\n    pass'
    response = await run_python(code)
    assert response == Response(
        stdout='', stderr=f'Timeout Error. Exceeded {TIMEOUT}s', exit_code=-1
    )


async def test_max_mem_test(run_python):
    code = f"x = ' ' * {CGROUP_MEM_MAX + 1_000}"
    response = await run_python(code)
    assert response == Response(stdout='', stderr='', exit_code=137)


async def test_write_file_to_sandbox_and_tmp(run_python):
    code = """from pathlib import Path

Path('/sandbox/blabla.txt').write_text('bla bla bla')
Path('/tmp/blabla.txt').write_text('bla bla bla')
"""
    response = await run_python(code)
    assert response == Response(stdout='', stderr='', exit_code=0)


async def test_write_in_protected_dirs(run_python):
    code = """from pathlib import Path

count = 0
for path in ['/', '/bin', '/etc', '/lib', '/lib64', '/usr']:
    try:
        Path(path, 'test.txt').write_text('test')
    except OSError:
        count += 1

print(count)
"""
    assert (await run_python(code)).stdout == '6\n'


async def test_forkbomb_recode_unavailable(run_python):
    code = """import os
while 1:
    os.fork()
    """
    resp = await run_python(code)
    assert 'BlockingIOError: [Errno 11] Resource temporarily unavailable' in resp.stderr
    assert resp.exit_code != 0


async def test_multiprocessing_shared_memory_disabled(run_python):
    code = """
from multiprocessing.shared_memory import SharedMemory

try:
    SharedMemory('test', create=True, size=16)
except FileExistsError:
    pass
"""
    resp = await run_python(code)
    assert 'OSError: [Errno' in resp.stderr
    assert resp.exit_code != 0


@flaky(max_runs=3)
async def test_subprocess_resource_unavailable(run_python) -> None:
    code = f"""\
import subprocess

for _ in range({CGROUP_PIDS_MAX * 2}):
    print(subprocess.Popen(
        [
            '/venv/bin/python',
            '-c',
            'import time; time.sleep(1)'
        ],
    ).pid)
"""
    resp = await run_python(code)
    assert resp.stderr
    assert resp.exit_code != 0


@flaky(max_runs=3)
async def test_multiprocess_resource_limits(run_python) -> None:
    code = f"""\
import time
from multiprocessing import Process

def f():
    object = "A" * {CGROUP_MEM_MAX + 1_000}
    time.sleep(0.5)

procs = []
for _ in range({CGROUP_PIDS_MAX + 1}):
    procs.append(Process(target=f))

for i in range({CGROUP_PIDS_MAX + 1}):
    procs[i].start()

for i in range({CGROUP_PIDS_MAX + 1}):
    procs[i].join()

for i in range({CGROUP_PIDS_MAX + 1}):
    print(procs[i].exitcode)
"""
    resp = await run_python(code, timeout=1.0)
    assert 'BlockingIOError: [Errno 11] Resource temporarily unavailable' in resp.stderr
    assert resp.exit_code != 0
