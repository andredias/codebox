import os
from pathlib import Path
from subprocess import check_call

from pytest import mark, raises

from app.utils import SandboxDirectory, inside_container, save_source


def test_sandbox():
    previous_dir = Path.cwd()
    with SandboxDirectory(dir='/dev/shm') as sandbox:
        assert Path.cwd() == sandbox
    assert Path.cwd() == previous_dir


def test_save_sources():
    contents = 'print("Hello")'
    with SandboxDirectory(dir='/dev/shm') as sandbox:
        save_source(sandbox, '/app/hello.py', contents)
        path = Path(sandbox, 'app/hello.py')
        assert path.exists()
        assert path.read_text() == contents

        with raises(ValueError):
            save_source(sandbox, 'test/../../../usr/bin/malicious.py', '')

        # surprisingly, this not raises an error
        save_source(sandbox, 'test/"blabla":*?\n/test.py', '')


INSIDE_GITHUB_ACTIONS = bool(os.environ.get('INSIDE_GITHUB_ACTIONS'))


@mark.skipif(INSIDE_GITHUB_ACTIONS, reason="It doesn't work in GitHub Actions")
def test_not_inside_container():
    assert not inside_container()


@mark.skipif(INSIDE_GITHUB_ACTIONS, reason="It doesn't work in GitHub Actions")
def test_inside_container(docker):
    check_call(
        'docker exec -it codebox '
        'python -c "from app.utils import inside_container; '
        'assert inside_container()"',
        shell=True,
    )
