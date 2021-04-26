import json
import sys

from .codebox import run_project
from .models import ProjectCore


def main():
    project = ProjectCore.parse_raw(sys.stdin.read())
    responses = run_project(project.sources, project.commands)
    responses = [resp.dict() for resp in responses]
    output = json.dumps(responses, ensure_ascii=False)
    print(output)
    return


if __name__ == '__main__':
    main()
