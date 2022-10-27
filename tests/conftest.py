import os
from collections.abc import AsyncIterable

import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import AsyncClient
from pytest import fixture

from app.main import app as _app
from app.utils import inside_container

os.environ['ENV'] = 'testing'


@fixture(scope='session')
def ensure_container() -> None:
    """
    Ensure that the code is executed inside a container.
    """
    if not inside_container():
        pytest.exit('This code must be executed inside a container.')
    return


@fixture(scope='session')
async def app(ensure_container) -> AsyncIterable[FastAPI]:
    """
    Create a FastAPI instance.
    """
    async with LifespanManager(_app):
        yield _app


@fixture
async def client(app: FastAPI) -> AsyncIterable[AsyncClient]:
    async with AsyncClient(
        app=app,
        base_url='http://codebox',
        headers={'Content-Type': 'application/json'},
    ) as client:
        yield client
