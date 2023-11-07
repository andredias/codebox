from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from . import config
from .logging import init_loguru
from .utils import inside_container


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator:  # noqa: ARG001
    await startup()
    try:
        yield
    finally:
        await shutdown()


async def startup() -> None:
    if not inside_container():
        raise RuntimeError('This code must be executed inside a container.')
    init_loguru()
    show_config()
    # insert here calls to connect to database and other services
    logger.info('started...')


async def shutdown() -> None:
    # insert here calls to disconnect from database and other services
    logger.info('...shutdown')


def show_config() -> None:
    config_vars = {key: getattr(config, key) for key in sorted(dir(config)) if key.isupper()}
    logger.debug('config vars', **config_vars)
