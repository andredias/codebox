from httpx import AsyncClient
from pytest import fixture

from app.models import Command, ProjectCore, Response


@fixture
def run_bash(client: AsyncClient):
    async def _run_bash(code: str) -> Response:
        sources = {'test.sh': code}
        commands = [
            Command(command='/bin/bash test.sh', timeout=1, pids_max=2),
        ]
        resp = await client.post(
            '/execute', json=ProjectCore(sources=sources, commands=commands).dict()
        )
        return Response(**(resp.json()[0]))

    return _run_bash


async def test_hello_world(run_bash):
    code = 'echo -n "Ola mundo!"'
    resp = await run_bash(code)
    assert resp == Response(stdout='Ola mundo!', stderr='', exit_code=0)


async def test_isort(run_bash):
    code = """python --version
rustc --version
"""
    resp = await run_bash(code)
    assert len(resp.stdout.splitlines()) == 2
    assert resp.exit_code == 0
