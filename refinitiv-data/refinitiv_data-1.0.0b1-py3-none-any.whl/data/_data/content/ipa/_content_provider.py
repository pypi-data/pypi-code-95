from typing import Union, Any

import numpy as np
from numpy import iterable

from ._enums import Axis
from .._content_provider import RequestFactory
from ...delivery.data.endpoint import RequestMethod
from ...tools._common import ArgsParser

types_by_axis = {
    Axis.DATE: "datetime64",
    "startDate": "datetime64",
    "endDate": "datetime64",
    Axis.DELTA: float,
    Axis.EXPIRY: float,
    Axis.MONEYNESS: float,
    Axis.STRIKE: float,
    Axis.TENOR: float,
    "discountFactor": float,
    "ratePercent": float,
}


def get_type_by_axis(axis):
    axis_values_type = types_by_axis.get(axis)

    if not axis_values_type:
        raise ValueError(f"Cannot find axis's values type for axis {axis}.")

    return axis_values_type


def parse_value(value: Any) -> Union[float, int, np.datetime64]:
    if isinstance(value, str):
        try:
            value = int(value)
        except ValueError:
            pass
        else:
            return value

        try:
            value = np.datetime64(value)
        except ValueError:
            # maybe it is a float
            value = float(value)

    return value


value_arg_parser = ArgsParser(parse_value)
x_arg_parser = value_arg_parser
y_arg_parser = value_arg_parser


# ---------------------------------------------------------------------------
#   RequestFactory
# ---------------------------------------------------------------------------


def parse_universe(universe):
    retval = []

    if not iterable(universe):
        universe = [universe]

    # convert universe's objects into json
    for i, item in enumerate(universe):
        if not hasattr(item, "get_json"):
            item = item._kwargs.get("universe")

        retval.append(item.get_json())

    return retval


def parse_outputs(outputs):
    retval = []

    if not isinstance(outputs, list):
        outputs = [outputs]

    for item in outputs:
        if hasattr(item, "value"):
            item = item.value

        retval.append(item)

    return retval


universe_arg_parser = ArgsParser(parse_universe)
outputs_arg_parser = ArgsParser(parse_outputs)


class CurvesAndSurfacesRequestFactory(RequestFactory):
    def get_request_method(self, *_, **kwargs):
        return kwargs.get("method", RequestMethod.POST)

    def get_body_parameters(self, *_, **kwargs):
        universe = kwargs.get("universe") or []
        outputs = kwargs.get("outputs")

        body_parameters = {}

        # universe
        universe = universe_arg_parser.get_list(universe)
        body_parameters["universe"] = universe

        # outputs
        if outputs:
            outputs = outputs_arg_parser.get_list(outputs)
            body_parameters["outputs"] = outputs

        return body_parameters
