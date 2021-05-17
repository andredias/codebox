from typing import Optional

import orjson
from pydantic import BaseModel as _BaseModel

from . import config

# ref: https://pydantic-docs.helpmanual.io/usage/exporting_models/#custom-json-deserialisation


def orjson_dumps(v, *, default):
    # orjson.dumps returns bytes, to match standard json.dumps we need to decode
    return orjson.dumps(v, default=default).decode()


class BaseModel(_BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


Sourcefiles = dict[str, str]


class Command(BaseModel):
    command: str
    stdin: Optional[str] = None
    timeout: Optional[float] = config.TIMEOUT
    # new options below to accomodate Rust compiling restrictions
    # they are not necessary for Python programs
    mem_max: Optional[int] = config.CGROUP_MEM_MAX
    pids_max: Optional[int] = config.CGROUP_PIDS_MAX
    cgroups_enabled: Optional[bool] = True


class ProjectCore(BaseModel):
    sources: Sourcefiles
    commands: list[Command]


class Response(BaseModel):
    stdout: str = ''
    stderr: str = ''
    exit_code: int = 0
