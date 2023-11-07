import asyncio

import pytest
from httpx import AsyncClient

from codebox.models import Command, ProjectCore, Response


@pytest.mark.parametrize('path', ['/execute', '/execute_insecure'])
async def test_multiple_calls(client: AsyncClient, path: str) -> None:
    async def call_run_project(code: str):
        sources = {'test.py': code}
        command = Command(command='/venv/bin/python test.py')
        resp = await client.post(
            path, json=ProjectCore(sources=sources, commands=[command]).model_dump()
        )
        return Response(**(resp.json()[0]))

    tasks = []
    for i in range(10):
        tasks.append(call_run_project(f'print({i})'))
    await asyncio.gather(*tasks)
