from typing import Union, Dict

import pydantic

from classiq_interface.executor.quantum_instruction_set import QuantumInstructionSet
from classiq_interface.backend.ionq import ionq_quantum_program


class QuantumProgram(pydantic.BaseModel):
    syntax: QuantumInstructionSet = pydantic.Field(
        ..., description="The syntax of the circuit."
    )
    code: Union[str, ionq_quantum_program.IonqQuantumCircuit] = pydantic.Field(
        ..., description="The textual representation of the circuit"
    )

    @pydantic.validator("code")
    def load_quantum_program(cls, code: str, values: Dict):
        if not isinstance(code, str):
            return code

        syntax = values.get("syntax")
        if syntax == QuantumInstructionSet.IONQ:
            return ionq_quantum_program.IonqQuantumCircuit.parse_raw(code)

        return code
