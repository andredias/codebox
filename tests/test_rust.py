from pathlib import Path

from httpx import AsyncClient
from pytest import fixture

from app.models import Command, ProjectCore, Response


@fixture
def run_rust(client: AsyncClient):
    async def _run_rust(code: str) -> list[Response]:
        filename = 'code.rs'
        sources = {filename: code}
        commands = [
            Command(command=f'/usr/local/cargo/bin/rustc {filename}', timeout=0.5),
            Command(command=f'./{Path(filename).stem}', timeout=0.1),
        ]
        resp = await client.post(
            '/execute', json=ProjectCore(sources=sources, commands=commands).dict()
        )
        return [Response(**r) for r in resp.json()]

    return _run_rust


async def test_hello_world(run_rust):
    code = """\
fn main() {
    println!("Hello World!");
}
"""
    resp = await run_rust(code)
    assert sum(r.exit_code for r in resp) == 0
    assert resp[1].stdout == 'Hello World!\n'
