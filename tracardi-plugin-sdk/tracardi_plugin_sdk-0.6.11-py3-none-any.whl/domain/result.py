from typing import Any
from pydantic import BaseModel


class Result(BaseModel):
    port: str
    value: Any = None

    class Config:
        allow_mutation = False


class MissingResult(Result):
    pass


class VoidResult(Result):
    pass
