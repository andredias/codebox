import os
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory, gettempdir
from unittest.mock import patch


def _create_sandbox_dir(suffix=None, prefix=None, dir=None) -> str:
    tmpdir = Path(dir or gettempdir(), 'sandbox')
    tmpdir.mkdir()
    return str(tmpdir)


class SandboxDirectory(TemporaryDirectory):
    """
    Extends TemporaryDirectory to automatically change to directory on enter
    and change it back on exit.
    Also, uses the fixed name of 'sandbox' during TESTING to make them possible
    since the temporary directory name might be part of the response traceback.
    """

    def __init__(self, *args, **kwargs):
        if 'TESTING' in os.environ:
            with patch('tempfile.mkdtemp', wraps=_create_sandbox_dir):
                super().__init__(*args, **kwargs)
        else:
            kwargs.setdefault('prefix', 'sandbox_')
            super().__init__(*args, **kwargs)
        return

    def __enter__(self):
        self.prev_dir = Path.cwd()
        os.chdir(self.name)
        return Path(self.name)

    def __exit__(self, exc_type, exc_value, traceback):
        os.chdir(self.prev_dir)
        super().__exit__(exc_type, exc_value, traceback)


def save_source(dest_dir: Path, filepath: str, contents: str) -> None:
    path = (dest_dir / filepath.lstrip(os.sep)).resolve()
    # checks for malicious or malformed paths
    if not str(path).startswith(str(dest_dir)):
        raise ValueError(f'Invalid file path: {path}')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents)


def inside_container() -> bool:
    """
    The developer's machine is not sandboxed and should not run any testing snippets,
    at the risk of being damaged.
    So, it is important to make sure that the code execution only happens inside a container.

    See:
    * https://stackoverflow.com/questions/23513045/how-to-check-if-a-process-is-running-inside-docker-container  # noqa: E501
    * https://stackoverflow.com/a/25518538/266362
    """
    return (
        Path('/.dockerenv').exists()
        or Path('/run/.containerenv').exists()
        or bool(run(['grep', ':/docker', '/proc/1/cgroup'], capture_output=True, text=True).stdout)
    )
