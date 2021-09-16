from typing import Set, Type

from classiq_interface.generator.arithmetic import (
    BitwiseAnd,
    BitwiseOr,
    BitwiseXor,
    Adder,
    Arithmetic,
    Equal,
    ArithmeticOracle,
    Negation,
)
from classiq_interface.generator.finance import Finance
from classiq_interface.generator.function_params import FunctionParams
from classiq_interface.generator.grover_operator import GroverOperator
from classiq_interface.generator.hadamard_amp_load import HadamardAmpLoad
from classiq_interface.generator.integer_comparator import IntegerComparator
from classiq_interface.generator.qaoa_ansatz import QaoaAnsatz
from classiq_interface.generator.qft import QFT
from classiq_interface.generator.sparse_amp_load import SparseAmpLoad
from classiq_interface.generator.state_preparation import StatePreparation
from classiq_interface.generator.state_propagator import StatePropagator
from classiq_interface.generator.entangler_params import TwoDimensionalEntangler
from classiq_interface.generator.vqe_ansatz import VQEAnsatz
from classiq_interface.generator.amplitude_estimation import AmplitudeEstimation
from classiq_interface.generator.entangler_params import HypercubeEntangler
from classiq_interface.generator.entangler_params import GridEntangler
from classiq_interface.generator.mcx import Mcx
from classiq_interface.generator.custom_function import CustomFunction


_function_param_list = {
    StatePreparation,
    VQEAnsatz,
    QaoaAnsatz,
    StatePropagator,
    QFT,
    BitwiseAnd,
    BitwiseOr,
    BitwiseXor,
    Adder,
    Arithmetic,
    ArithmeticOracle,
    Equal,
    Negation,
    TwoDimensionalEntangler,
    IntegerComparator,
    Finance,
    HypercubeEntangler,
    AmplitudeEstimation,
    SparseAmpLoad,
    GridEntangler,
    HadamardAmpLoad,
    GroverOperator,
    Mcx,
    CustomFunction,
}


def get_function_param_list() -> Set[Type[FunctionParams]]:
    return _function_param_list
