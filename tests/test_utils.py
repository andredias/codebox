from pathlib import Path

from pytest import raises

from app.utils import SandboxDirectory, save_source


def test_sandbox():
    previous_dir = Path.cwd()
    with SandboxDirectory() as sandbox:
        assert Path.cwd() == sandbox
    assert Path.cwd() == previous_dir


def test_save_sources():
    contents = 'print("Hello")'
    with SandboxDirectory() as sandbox:
        save_source(sandbox, '/app/hello.py', contents)
        path = Path(sandbox, 'app/hello.py')
        assert path.exists()
        assert path.read_text() == contents

        with raises(ValueError):
            save_source(sandbox, 'test/../../../usr/bin/malicious.py', '')

        # surprisingly, this not raises an error
        save_source(sandbox, 'test/"blabla":*?\n/test.py', '')
