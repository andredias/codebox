from typing import Optional

from pydantic import BaseModel


class Lint(BaseModel):
    line: int
    column: Optional[int]
    code: str
    message: str
    level: str
    linter: str


class Metric(BaseModel):
    name: str
    value: float


Sourcefiles = dict[str, str]


class CommandIn(BaseModel):
    type: str
    command: str
    timeout: Optional[float] = None
    input: Optional[str] = None


class CommandOut(BaseModel):
    type: str
    command: str
    stdout: Optional[str] = None
    stderr: Optional[str] = None


class ProjectOut(BaseModel):
    id: str


class ProjectCore(BaseModel):
    sources: Sourcefiles
    commands: list[CommandIn]


class ProjectIn(ProjectCore):
    title: str = ''
    description: str = ''


class Project(ProjectIn, ProjectOut):
    pass
