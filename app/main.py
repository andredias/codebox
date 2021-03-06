import sys

from fastapi import FastAPI
from loguru import logger

from . import config
from .codebox import run_project
from .models import ProjectCore, Response
from .utils import available_languages, inside_container

app = FastAPI()


@app.post('/execute', response_model=list[Response])
def execute(project: ProjectCore):
    responses = run_project(project.sources, project.commands)
    return responses


@app.get('/languages')
def languages():
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
