# coding: utf8

__all__ = ["ForwardCurveRequestItem"]

from ....tools import ArgsParser
from ._forward_curve_definition import ForwardCurveDefinition
from ._swap_zc_curve_definition import SwapZcCurveDefinition
from ._swap_zc_curve_parameters import SwapZcCurveParameters
from ._forward_curve_types import (
    OptStr,
    CurveDefinition,
    CurveParameters,
    ForwardCurveDefinitions,
)
from .._object_definition import ObjectDefinition


def parse_forward_curve_definitions(
    param: ForwardCurveDefinitions,
) -> ForwardCurveDefinitions:
    if not param:
        return param

    if not isinstance(param, list):
        param = [param]

    return param


forward_curve_definitions_arg_parser = ArgsParser(parse_forward_curve_definitions)


class ForwardCurveRequestItem(ObjectDefinition):
    """
    Parameters
    ----------
    curve_definition : SwapZcCurveDefinition, optional

    curve_parameters : SwapZcCurveParameters, optional

    forward_curve_definitions : list of ForwardCurveDefinition, optional

    curve_tag : str, optional

    """

    def __init__(
        self,
        curve_definition: CurveDefinition = None,
        forward_curve_definitions: ForwardCurveDefinitions = None,
        curve_parameters: CurveParameters = None,
        curve_tag: OptStr = None,
    ) -> None:
        super().__init__()
        self.curve_definition = curve_definition
        self.curve_parameters = curve_parameters
        self.forward_curve_definitions = forward_curve_definitions_arg_parser.parse(
            forward_curve_definitions
        )
        self.curve_tag = curve_tag

    @property
    def curve_definition(self):
        """
        :return: object SwapZcCurveDefinition
        """
        return self._get_object_parameter(SwapZcCurveDefinition, "curveDefinition")

    @curve_definition.setter
    def curve_definition(self, value):
        self._set_object_parameter(SwapZcCurveDefinition, "curveDefinition", value)

    @property
    def curve_parameters(self):
        """
        :return: object SwapZcCurveParameters
        """
        return self._get_object_parameter(SwapZcCurveParameters, "curveParameters")

    @curve_parameters.setter
    def curve_parameters(self, value):
        self._set_object_parameter(SwapZcCurveParameters, "curveParameters", value)

    @property
    def forward_curve_definitions(self):
        """
        :return: list ForwardCurveDefinition
        """
        return self._get_list_parameter(
            ForwardCurveDefinition, "forwardCurveDefinitions"
        )

    @forward_curve_definitions.setter
    def forward_curve_definitions(self, value):
        self._set_list_parameter(
            ForwardCurveDefinition, "forwardCurveDefinitions", value
        )

    @property
    def curve_tag(self):
        """
        :return: str
        """
        return self._get_parameter("curveTag")

    @curve_tag.setter
    def curve_tag(self, value):
        self._set_parameter("curveTag", value)
