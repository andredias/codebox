import os
from functools import cache
from pathlib import Path
from subprocess import check_output, run
from tempfile import TemporaryDirectory


class SandboxDirectory(TemporaryDirectory):
    """
    Extends TemporaryDirectory to automatically change to directory on enter
    and change it back on exit.
    Also, uses the fixed name of 'sandbox' during TESTING to make them possible
    since the temporary directory name might be part of the response traceback.
    """

    def __init__(self, *args, **kwargs):
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


@cache
def available_languages() -> dict[str, str]:
    def get_version(lang_name: str) -> list[str]:
        resp = check_output((lang_name, '--version'), text=True)
        return resp.split()

    languages = {}
    languages['python'] = get_version('python')[1]
    languages['rust'] = get_version('rustc')[1]
    languages['sqlite3'] = get_version('sqlite3')[0]
    languages['bash'] = get_version('bash')[3]

    return languages
