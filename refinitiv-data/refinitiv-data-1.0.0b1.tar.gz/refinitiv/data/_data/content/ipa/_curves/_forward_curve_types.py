from typing import Optional, Iterable, Union, TYPE_CHECKING

from ..._types import Strings, OptStr, ExtendedParams, OptStrings, OptFloat, OptInt

if TYPE_CHECKING:
    from ._swap_zc_curve_definition import SwapZcCurveDefinition
    from ._swap_zc_curve_parameters import SwapZcCurveParameters
    from ._forward_curve_definition import ForwardCurveDefinition
    from .. import forward_curve
    from ._enums import ForwardCurvesOutputs

CurveDefinition = Optional["SwapZcCurveDefinition"]
CurveParameters = Optional["SwapZcCurveParameters"]
ForwardCurveDefinitions = Union[
    "ForwardCurveDefinition", Iterable["ForwardCurveDefinition"]
]

Outputs = Union[Strings, Iterable["ForwardCurvesOutputs"]]
Universe = Union["forward_curve.Definition", Iterable["forward_curve.Definition"]]

Steps = Union[Iterable["Step"]]
Turns = Union[Iterable["Turn"]]
