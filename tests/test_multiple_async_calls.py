import asyncio

from httpx import AsyncClient

from app.models import Command, ProjectCore, Response


async def test_multiple_calls(client: AsyncClient) -> None:
    async def call_run_project(code: str):
        sources = {'test.py': code}
        command = Command(command='/venv/bin/python test.py')
        resp = await client.post(
            '/execute', json=ProjectCore(sources=sources, commands=[command]).dict()
        )
        return Response(**(resp.json()[0]))

    tasks = []
    for i in range(10):
        tasks.append(call_run_project(f'print({i})'))
    await asyncio.gather(*tasks)
