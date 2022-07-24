import os
from functools import cache
from pathlib import Path
from subprocess import check_output, run


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
