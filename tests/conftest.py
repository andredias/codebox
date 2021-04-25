import os
from pathlib import Path
from subprocess import run

import pytest

os.environ['TESTING'] = 'yes'


def inside_container() -> bool:
    """
    The developer's machine is not sandboxed and should not run any testing snippets, at the risk of being damaged.
    So, it is important to make sure that the code execution only happens inside a container.

    See:
    * https://stackoverflow.com/questions/23513045/how-to-check-if-a-process-is-running-inside-docker-container
    * https://stackoverflow.com/a/25518538/266362
    """
    return (
        Path('/.dockerenv').exists()
        or Path('/run/.containerenv').exists()
        or bool(run(['grep', ':/docker', '/proc/1/cgroup'], capture_output=True, text=True).stdout)
    )


run_inside_container = pytest.mark.skipif(not inside_container(), reason='not running inside a container')
run_outside_container = pytest.mark.skipif(inside_container(), reason='running inside a container')
