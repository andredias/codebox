from pathlib import Path
from tempfile import TemporaryDirectory

from pytest import raises

from app.utils import save_source


def test_save_sources():
    contents = 'print("Hello")'
    with TemporaryDirectory(prefix='sandbox_') as sandbox:
        sandbox = Path(sandbox)
        save_source(sandbox, '/app/hello.py', contents)
        path = sandbox / 'app/hello.py'
        assert path.exists()
        assert path.read_text() == contents

        with raises(ValueError):
            save_source(sandbox, 'test/../../../usr/bin/malicious.py', '')

        # surprisingly, this not raises an error
        save_source(sandbox, 'test/"blabla":*?\n/test.py', '')
