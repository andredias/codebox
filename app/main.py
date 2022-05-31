import sys

from fastapi import Body, FastAPI
from loguru import logger

from . import config
from .codebox import run_project
from .models import ProjectCore, Response

app = FastAPI()


@app.post('/execute', response_model=list[Response])
def execute(project: ProjectCore):
    responses = run_project(project.sources, project.commands)
    return responses


@app.post('/python', response_model=Response)
def run_python(code: str = Body()):
    from .nsjail.nsjail import NsJail

    resp = NsJail().python3(code)
    logger.debug(resp)
    return Response(stdout=resp.stdout, stderr=resp.stderr, exit_code=resp.returncode)


@app.on_event('startup')
async def startup_event():
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
