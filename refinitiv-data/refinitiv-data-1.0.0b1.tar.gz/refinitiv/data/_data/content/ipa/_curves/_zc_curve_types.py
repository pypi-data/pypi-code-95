from typing import Iterable, Union, TYPE_CHECKING, Optional

from ..._types import Strings

if TYPE_CHECKING:
    from ._models import Step, Turn, Constituents
    from ._zc_curve_parameters import ZcCurveParameters
    from ._zc_curve_definitions import ZcCurveDefinitions
    from ._enums import ZcCurvesOutputs

Steps = Union[Iterable["Step"]]
Turns = Union[Iterable["Turn"]]
OptConstituents = Optional["Constituents"]
CurveDefinition = Optional["ZcCurveDefinitions"]
CurveParameters = Optional["ZcCurveParameters"]
Universe = Union["zc_curve.Definition", Iterable["zc_curve.Definition"]]
Outputs = Union[Strings, Iterable["ZcCurvesOutputs"]]
