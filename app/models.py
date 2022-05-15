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


class ProjectCore(BaseModel):
    sources: Sourcefiles
    commands: list[Command]


class Response(BaseModel):
    stdout: str = ''
    stderr: str = ''
    exit_code: int = 0
