from typing import Optional, Dict

import pydantic

from classiq_interface.backend.backend_preferences import (
    IonqBackendPreferences,
)
from classiq_interface.executor.execution_preferences import ExecutionPreferences
from classiq_interface.executor.quantum_program import QuantumProgram
from classiq_interface.generator.generation_metadata import GenerationMetadata


class ExecutionRequest(pydantic.BaseModel):
    preferences: ExecutionPreferences = pydantic.Field(
        default_factory=ExecutionPreferences,
        description="preferences for the execution",
    )

    problem_data: Optional[GenerationMetadata] = pydantic.Field(
        default=None, description="Data returned from the generation procedure."
    )
    quantum_program: Optional[QuantumProgram] = pydantic.Field(
        default=None,
        description="The quantum program to execute.",
    )

    @pydantic.root_validator()
    def validate_mutual_exclusive_fields(cls, values: Dict) -> Dict:
        is_problem_data_defined = values.get("problem_data") is not None
        is_quantum_program_defined = values.get("quantum_program") is not None

        has_exactly_one_mandatory_field_defined = (
            is_problem_data_defined ^ is_quantum_program_defined
        )
        if not has_exactly_one_mandatory_field_defined:
            raise ValueError(
                "Exactly one of quantum_program and problem_data should be defined."
            )

        return values

    @pydantic.validator("quantum_program")
    def validate_supported_backends(cls, quantum_program, values: Dict):
        if quantum_program is None:
            return quantum_program

        problem_preferences = values.get("preferences")
        if not isinstance(
            problem_preferences.backend_preferences, IonqBackendPreferences
        ):
            raise ValueError("Currently, only IonQ is supported for generic execution.")

        return quantum_program
