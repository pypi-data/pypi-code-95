import enum
from typing import List

import pydantic

from classiq_interface.generator.complex_type import Complex


class PauliOperator(pydantic.BaseModel):
    str: str
    table: List[List[bool]]
    coeffs: List[Complex]

    def show(self) -> str:
        return self.str


class OperatorStatus(str, enum.Enum):
    SUCCESS = "success"
    ERROR = "error"


class OperatorResult(pydantic.BaseModel):
    status: OperatorStatus
    details: PauliOperator
