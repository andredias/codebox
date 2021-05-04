import os
from pathlib import Path
from subprocess import DEVNULL, check_call
from time import sleep
from typing import AsyncIterable, Generator

from httpx import AsyncClient
from pytest import fixture

os.environ['ENV'] = 'testing'


@fixture(scope='session')
def docker() -> Generator:
    app_dir = Path(__file__).parent.parent / 'app'
    check_call(
        f'docker run -d --privileged --rm -p 8001:8000 -v {app_dir}:/codebox/app '
        '-e ENV=development --name codebox-testing codebox',
        stdout=DEVNULL,
        shell=True,
    )
    sleep(1)
    try:
        yield
    finally:
        check_call('docker stop -t 0 codebox-testing', stdout=DEVNULL, shell=True)


@fixture
async def client(docker) -> AsyncIterable[AsyncClient]:
    async with AsyncClient(base_url='http://localhost:8001') as client:
        yield client
