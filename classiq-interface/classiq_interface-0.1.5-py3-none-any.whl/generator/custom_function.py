from enum import Enum
from typing import Type, List

import pydantic
from classiq_interface.generator.custom_implementation import CustomImplementation
from classiq_interface.generator.function_params import FunctionParams


class CustomFunctionInputs(Enum):
    CUSTOM_FUNCTION_INPUT = "CUSTOM_FUNCTION_INPUT"


class CustomFunctionOutputs(Enum):
    CUSTOM_FUNCTION_OUTPUT = "CUSTOM_FUNCTION_OUTPUT"


class CustomFunction(FunctionParams):
    """
    Facilitates the creation of a user-defined custom function
    """

    class Config:
        # Perform validation on assignment to attributes
        validate_assignment = True

    name: str = pydantic.Field(description="The name of a custom function")

    num_io_qubits: pydantic.conint(ge=1) = pydantic.Field(
        description="The number of IO qubits of a custom function"
    )

    custom_implementations: List[CustomImplementation] = pydantic.Field(
        description="The implementations of a custom function"
    )

    _input_names: Type[Enum] = pydantic.PrivateAttr(default=CustomFunctionInputs)
    _output_names: Type[Enum] = pydantic.PrivateAttr(default=CustomFunctionOutputs)

    @pydantic.validator("custom_implementations", each_item=True)
    def validate_custom_implementations(
        cls, custom_implementation: CustomImplementation, values
    ):
        if custom_implementation._num_qubits_in_qasm is None:
            return custom_implementation
        if custom_implementation._num_qubits_in_qasm < values["num_io_qubits"]:
            raise ValueError(
                f"The number of qubits in the quantum circuit of the implementation {custom_implementation.name} is incompatible with the function."
            )
        return custom_implementation
