import os as _os

from .installation import iai_run_julia_setup


def _iai_version_less_than(version):
    jleval = _Main.string("Base.thispatch(v\"", _Main.iai_version, "\")",
                          " < ",
                          "Base.thispatch(v\"", version, "\")")
    return _Main.eval(jleval)


def _requires_iai_version(required_iai_version, function_name, extra=''):
    if _iai_version_less_than(required_iai_version):
        raise RuntimeError(
            "The function `" + function_name + "` " + extra + " in this " +
            "version of the `interpretableai` Python package requires IAI " +
            "version " + required_iai_version + ". Please upgrade your IAI " +
            "installation to use this function.")


_Main = iai_run_julia_setup()


# Run Julia setup code
_script_dir = _os.path.dirname(_os.path.realpath(__file__))
try:
    _Main.include(_os.path.join(_script_dir, "setup.jl"))
except ImportError as err:
    msg = str(err)

    # Trim Julia stacktrace from message
    # Message format depends on PyCall version
    if msg.startswith("Julia exception"):  # pragma: no cover
        line_index = 0
    else:
        line_index = 1
    msg = str(err).split("\n")[line_index]

    from future.utils import raise_from
    raise_from(ImportError(msg), None)


# Hack to get a reference to IAI without `import`
import julia as _julia
_IAI = _julia.core.JuliaModuleLoader().load_module("Main.IAI")


from julia import Random as _Random
def set_julia_seed(*args):
    """Set the random seed in Julia to `seed`.

    Julia Equivalent:
    `Random.seed! <https://docs.julialang.org/en/v1/stdlib/Random/index.html#Random.seed!>`

    Examples
    --------
    >>> iai.set_julia_seed(seed)
    """
    return _Random.seed_b(*args)


from julia import Distributed as _Distributed
def add_julia_processes(*args):
    """Add additional Julia worker processes to parallelize workloads.

    Julia Equivalent:
    `Distributed.addprocs <https://docs.julialang.org/en/v1/stdlib/Distributed/#Distributed.addprocs>`

    For more information, refer to the
    `documentation on parallelization <https://docs.interpretable.ai/stable/IAIBase/advanced/#IAIBase-Parallelization-1>`

    Examples
    --------
    >>> iai.add_julia_processes(3)
    """
    out = _Distributed.addprocs(*args)

    # We need to load IAI on all processes
    # NB: If using system image this is automatic
    if not _Main.eval('isdefined(Main, :IAISysImg)'):
        _Main.eval('import Distributed; Distributed.@everywhere import IAI')

    return out


def get_machine_id():
    """Return the machine ID for the current computer.

    Examples
    --------
    >>> iai.get_machine_id()
    """
    return _IAI.get_machine_id_convert()


def _get_learner_type(jl_obj):
    if _Main.isa(jl_obj, _IAI.OptimalTreeClassifier):
        L = OptimalTreeClassifier
    elif _Main.isa(jl_obj, _IAI.OptimalTreeRegressor):
        L = OptimalTreeRegressor
    elif (_iai_version_less_than("2.0.0") and
          _Main.isa(jl_obj, _IAI.OptimalTreeSurvivor)):
        L = OptimalTreeSurvivalLearner
    elif (not _iai_version_less_than("2.0.0") and
          _Main.isa(jl_obj, _IAI.OptimalTreeSurvivalLearner)):
        L = OptimalTreeSurvivalLearner
    elif _Main.isa(jl_obj, _IAI.OptimalTreePrescriptionMinimizer):
        L = OptimalTreePrescriptionMinimizer
    elif _Main.isa(jl_obj, _IAI.OptimalTreePrescriptionMaximizer):
        L = OptimalTreePrescriptionMaximizer
    elif (not _iai_version_less_than("2.0.0") and
          _Main.isa(jl_obj, _IAI.OptimalTreePolicyMinimizer)):
        L = OptimalTreePolicyMinimizer
    elif (not _iai_version_less_than("2.0.0") and
          _Main.isa(jl_obj, _IAI.OptimalTreePolicyMaximizer)):
        L = OptimalTreePolicyMaximizer
    elif _Main.isa(jl_obj, _IAI.OptimalFeatureSelectionClassifier):
        L = OptimalFeatureSelectionClassifier
    elif _Main.isa(jl_obj, _IAI.OptimalFeatureSelectionRegressor):
        L = OptimalFeatureSelectionRegressor
    elif _Main.isa(jl_obj, _IAI.OptKNNImputationLearner):
        L = OptKNNImputationLearner
    elif _Main.isa(jl_obj, _IAI.OptSVMImputationLearner):
        L = OptSVMImputationLearner
    elif _Main.isa(jl_obj, _IAI.OptTreeImputationLearner):
        L = OptTreeImputationLearner
    elif _Main.isa(jl_obj, _IAI.SingleKNNImputationLearner):
        L = SingleKNNImputationLearner
    elif _Main.isa(jl_obj, _IAI.MeanImputationLearner):
        L = MeanImputationLearner
    elif _Main.isa(jl_obj, _IAI.RandImputationLearner):
        L = RandImputationLearner
    elif (not _iai_version_less_than("2.1.0") and
          _Main.isa(jl_obj, _IAI.RandomForestClassifier)):
        L = RandomForestClassifier
    elif (not _iai_version_less_than("2.1.0") and
          _Main.isa(jl_obj, _IAI.RandomForestRegressor)):
        L = RandomForestRegressor
    elif (not _iai_version_less_than("2.1.0") and
          _Main.isa(jl_obj, _IAI.XGBoostClassifier)):
        L = XGBoostClassifier
    elif (not _iai_version_less_than("2.1.0") and
          _Main.isa(jl_obj, _IAI.XGBoostRegressor)):
        L = XGBoostRegressor
    elif (not _iai_version_less_than("2.3.0") and
          _Main.isa(jl_obj, _IAI.GLMNetCVClassifier)):
        L = GLMNetCVClassifier
    elif (not _iai_version_less_than("2.1.0") and
          _Main.isa(jl_obj, _IAI.GLMNetCVRegressor)):
        L = GLMNetCVRegressor

    return L


# Load all subpackages into main namespace
from .mixeddata import MixedData
from .iaibase import *
from .iaitrees import *
from .optimaltrees import *
from .optimpute import *
from .optimalfeatureselection import *
from .rewardestimation import *
from .heuristics import *
