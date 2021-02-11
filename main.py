import json
import sys

from app.codebox import run_project
from app.models import CodeboxInput


def main():
    project = CodeboxInput.parse_raw(sys.stdin.read())
    response = run_project(project.sources, project.commands)
    json.dump(response, sys.stdout)
    sys.exit(0)


if __name__ == '__main__':
    main()
