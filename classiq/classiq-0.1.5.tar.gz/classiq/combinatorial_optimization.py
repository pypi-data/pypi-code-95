from typing import Optional
from pyomo.core import ConcreteModel

from classiq_interface.backend.backend_preferences import (
    BackendPreferences,
    IBMBackendPreferences,
)
from classiq_interface.combinatorial_optimization import (
    model_serializer,
    optimization_problem,
)
from classiq_interface.generator.result import GenerationResult
from classiq_interface.hybrid import result as hybrid_result
from classiq_interface.generator import result as generator_result
from classiq_interface.hybrid import vqe_problem
from classiq import api_wrapper

from classiq_interface.hybrid.result import HybridResult


class CombinatorialOptimization:
    def __init__(
        self,
        model: ConcreteModel,
        vqe_preferences: Optional[vqe_problem.VQEPreferences] = None,
        backend_preferences: Optional[BackendPreferences] = None,
    ):
        if vqe_preferences is None:
            vqe_preferences = vqe_problem.VQEPreferences()
        if backend_preferences is None:
            backend_preferences = IBMBackendPreferences(
                backend_service_provider="IBMQ", backend_name="aer_simulator"
            )

        self._serialized_model = model_serializer.to_json(model, return_dict=True)
        self._problem = optimization_problem.OptimizationProblem(
            serialized_model=self._serialized_model,
            vqe_preferences=vqe_preferences,
            backend_preferences=backend_preferences,
        )

    async def generate(self) -> GenerationResult:
        wrapper = api_wrapper.ApiWrapper()
        result = await wrapper.call_combinatorial_optimization_generate_task(
            problem=self._problem
        )

        if result.status != generator_result.GenerationStatus.SUCCESS:
            raise Exception(f"Solving failed: {result.details}")

        return result

    async def solve(self) -> HybridResult:
        wrapper = api_wrapper.ApiWrapper()
        result = await wrapper.call_combinatorial_optimization_solve_task(
            problem=self._problem
        )

        if result.status != hybrid_result.HybridStatus.SUCCESS:
            raise Exception(f"Solving failed: {result.details}")

        return result
