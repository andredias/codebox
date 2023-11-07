from fastapi import APIRouter

from ..codebox import execute_insecure as exec_insec
from ..codebox import run_project
from ..models import ProjectCore, Response
from ..utils import available_languages

router = APIRouter()


@router.post('/execute')
def execute(project: ProjectCore) -> list[Response]:
    return run_project(project.sources, project.commands)


@router.post('/execute_insecure')
def execute_insecure(project: ProjectCore) -> list[Response]:
    return run_project(project.sources, project.commands, exec_func=exec_insec)


@router.get('/languages')
def languages() -> dict[str, str]:
    return available_languages()
