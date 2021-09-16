"""Custom function library module, implementing facilities for adding user defined functions to the Classiq platform."""
from typing import Dict

from classiq_interface.generator.custom_function import CustomFunction
from classiq_interface.generator.custom_implementation import CustomImplementation


class CustomFunctionLibrary:
    """Facility to manage user-defined custom functions."""

    def __init__(self, name: str = None):
        self._custom_functions_dict = dict()
        self._name = name

    def get_custom_function(self, function_name: str):
        """Gets a function from the function library.

        Args:
            function_name (): The name of the custom function.
        """
        if function_name not in self._custom_functions_dict:
            raise ValueError("Cannot fetch non-existing custom functions.")
        return self._custom_functions_dict[function_name]

    def add_custom_function_to_library(
        self,
        function_name: str,
        single_implementation_quantum_circuit_qasm_string: str,
        implementation_name: str = None,
        override_existing_custom_functions: bool = False,
    ) -> CustomFunction:
        """Adds a function to the function library.

        Args:
            function_name (): The name of the custom function.
            single_implementation_quantum_circuit_qasm_string (): A QASM code of the custom function.

        Returns:
            The custom function parameters.
        """
        if (
            not override_existing_custom_functions
            and function_name in self._custom_functions_dict
        ):
            raise ValueError("Cannot override existing custom functions.")

        custom_implementation = CustomImplementation(
            name=implementation_name,
            single_implementation_quantum_circuit_qasm_string=single_implementation_quantum_circuit_qasm_string,
        )

        num_qubits_in_qasm = custom_implementation._num_qubits_in_qasm

        custom_function = CustomFunction(
            name=function_name,
            custom_implementations=[custom_implementation],
            num_io_qubits=num_qubits_in_qasm,
        )

        self._custom_functions_dict[custom_function.name] = custom_function
        return custom_function

    def remove_custom_function_from_library(self, function_name: str) -> None:
        """Removes a function from the function library.

        Args:
            function_name (): The name of the custom function.
        """
        if function_name in self._custom_functions_dict:
            del self._custom_functions_dict[function_name]
        else:
            raise ValueError("Cannot remove non-exisiting custom functions.")

    @property
    def name(self) -> str:
        """Get the library name.

        Returns:
            The the library name.
        """
        return self._name
