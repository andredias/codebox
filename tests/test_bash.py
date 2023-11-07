from httpx import AsyncClient
from pytest import fixture

from codebox.models import Command, ProjectCore, Response


@fixture
def run_bash(client: AsyncClient):
    async def _run_bash(code: str) -> Response:
        sources = {'test.sh': code}
        commands = [
            Command(command='/bin/bash test.sh', timeout=0.1),
        ]
        resp = await client.post(
            '/execute', json=ProjectCore(sources=sources, commands=commands).model_dump()
        )
        return Response(**(resp.json()[0]))

    return _run_bash


async def test_hello_world(run_bash):
    code = 'echo -n "Ola mundo!"'
    resp = await run_bash(code)
    assert resp == Response(stdout='Ola mundo!', stderr='', exit_code=0)


async def test_get_version(run_bash):
    code = 'bash --version'
    resp = await run_bash(code)
    assert resp.exit_code == 0
    assert 'version' in resp.stdout.lower()


async def test_printenv(run_bash):
    code = '/usr/bin/printenv'
    resp = await run_bash(code)
    print(resp.stdout)
    assert resp.exit_code == 0
