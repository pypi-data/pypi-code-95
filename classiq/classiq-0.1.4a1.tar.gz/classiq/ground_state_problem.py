from classiq import api_wrapper

from classiq_interface.chemistry import ground_state_problem, operator
from classiq_interface.chemistry.operator import PauliOperator


async def generate_hamiltonian(
    gs_problem: ground_state_problem.GroundStateProblem,
) -> PauliOperator:
    wrapper = api_wrapper.ApiWrapper()
    result = await wrapper.call_generate_hamiltonian_task(problem=gs_problem)

    if result.status != operator.OperatorStatus.SUCCESS:
        raise Exception(f"Generate Hamiltonian failed: {result.details}")

    return result.details
