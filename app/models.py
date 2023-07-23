from pydantic import BaseModel

from . import config

# ref: https://pydantic-docs.helpmanual.io/usage/exporting_models/#custom-json-deserialisation


Sourcefiles = dict[str, str]


class Command(BaseModel):
    command: str
    stdin: str | None = None
    timeout: float | None = config.TIMEOUT


class ProjectCore(BaseModel):
    sources: Sourcefiles
    commands: list[Command]


class Response(BaseModel):
    stdout: str | None = ''
    stderr: str | None = ''
    exit_code: int = 0
    elapsed_time: float = 0

    def __str__(self) -> str:
        return (
            f'Response(stdout={self.stdout!r}, stderr={self.stderr!r}, '
            f'exit_code={self.exit_code!r}, elapsed_time={self.elapsed_time * 1000:.0f}ms)'
        )

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Response)
            and self.stdout == other.stdout
            and self.stderr == other.stderr
            and self.exit_code == other.exit_code
            # elapsed_time is not compared because it is not guaranteed to be the same
        )
