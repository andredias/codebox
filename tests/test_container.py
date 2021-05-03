from subprocess import run

from pydantic import parse_raw_as
from pytest import mark

from app.models import ProjectCore, Response

from .conftest import projects, run_outside_container

# Skip all test functions of a module
pytestmark = run_outside_container


def run_project_in_container(project_core: ProjectCore) -> list[Response]:
    """
    Run the project in a sandbox container
    """
    project_json = project_core.json(exclude_unset=True)
    docker_cmd = ['docker', 'run', '-i', '--rm', '--privileged', '-v', '/tmp:/tmp', 'codebox']
    proc = run(docker_cmd, input=project_json, capture_output=True, text=True)
    assert proc.stderr == ''
    result = parse_raw_as(list[Response], proc.stdout)
    return result


@mark.parametrize('sources,commands,responses', projects)
def test_launch_container(sources, commands, responses):
    assert run_project_in_container(ProjectCore(sources=sources, commands=commands)) == responses
