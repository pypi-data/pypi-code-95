"""Executor module, implementing facilities for executing quantum programs using Classiq platform."""
from typing import Union, Optional

import classiq_interface.executor.execution_preferences
from classiq import api_wrapper
from classiq_interface.executor import result as exc_result, execution_request
from classiq_interface.executor.result import (
    FinanceSimulationResults,
    GroverSimulationResults,
    ExecutionDetails,
)
from classiq_interface.generator import result as gen_result


class Executor:
    """Executor is the entry point for executing quantum programs on multiple quantum hardware vendors."""

    def __init__(
        self,
        preferences: classiq_interface.executor.execution_preferences.ExecutionPreferences,
        quantum_program: Optional[
            classiq_interface.executor.quantum_program.QuantumProgram
        ] = None,
        generation_result: Optional[gen_result.GeneratedCircuit] = None,
    ) -> None:
        """Init self.

        Args:
            quantum_program (): The quantum program to execute.
            preferences (): Execution preferences, such as number of shots.
            generation_result (): The result of a previous Classiq generation task.
        """
        self._request = execution_request.ExecutionRequest(
            quantum_program=quantum_program,
            preferences=preferences,
            problem_data=generation_result.metadata
            if generation_result is not None
            else None,
        )

    # TODO needs to be changed to execution result
    async def execute(
        self,
    ) -> Union[ExecutionDetails, FinanceSimulationResults, GroverSimulationResults]:
        """Executes the circuit and returns its results.

        Returns:
            The execution results, corresponding to the executed circuit type.
        """
        wrapper = api_wrapper.ApiWrapper()
        execute_result = await wrapper.call_execute_task(request=self._request)

        if execute_result.status != exc_result.ExecutionStatus.SUCCESS:
            raise Exception(f"Execution failed: {execute_result.details}")

        return execute_result.details
