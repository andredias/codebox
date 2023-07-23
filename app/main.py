import sys

from fastapi import FastAPI
from loguru import logger

from . import config
from .codebox import execute_insecure as exec_insec
from .codebox import run_project
from .models import ProjectCore, Response
from .utils import available_languages, inside_container

app = FastAPI()


@app.post('/execute')
def execute(project: ProjectCore) -> list[Response]:
    return run_project(project.sources, project.commands)


@app.post('/execute_insecure')
def execute_insecure(project: ProjectCore) -> list[Response]:
    return run_project(project.sources, project.commands, exec_func=exec_insec)


@app.get('/languages')
def languages() -> dict[str, str]:
    return available_languages()


@app.on_event('startup')
async def startup_event():
    if not inside_container():
        raise RuntimeError('This code must be executed inside a container.')
    setup_logger()


@app.on_event('shutdown')
async def shutdown_event():
    ...


def setup_logger():
    """
    Configure Loguru's logger
    """
    logger.remove()  # remove standard handler
    logger.add(
        sys.stderr, level=config.LOG_LEVEL, colorize=True, backtrace=config.DEBUG, enqueue=True
    )  # reinsert it to make it run in a different thread
