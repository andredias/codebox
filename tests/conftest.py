import os
from pathlib import Path
from subprocess import DEVNULL, check_call, check_output
from time import sleep
from typing import AsyncIterable, Generator

from httpx import AsyncClient
from pytest import fixture

os.environ['ENV'] = 'testing'


@fixture(scope='session')
def docker() -> Generator:
    # check if there is a running docker container
    output = check_output('docker container ls -q -f name=^codebox$', shell=True)
    if output:
        # container is running
        yield
        return

    app_dir = Path(__file__).parent.parent / 'app'
    check_call(
        'docker run -d -v /sys/fs/cgroup:/sys/fs/cgroup '
        f'--privileged --rm -p 8000:8000 -v {app_dir}:/codebox/app '
        '--ipc=none -e ENV=development --name codebox codebox',
        stdout=DEVNULL,
        shell=True,
    )
    sleep(1)
    try:
        yield
    finally:
        check_call('docker stop -t 0 codebox', stdout=DEVNULL, shell=True)


@fixture
async def client(docker) -> AsyncIterable[AsyncClient]:
    async with AsyncClient(base_url='http://localhost:8000', timeout=None) as client:
        yield client
