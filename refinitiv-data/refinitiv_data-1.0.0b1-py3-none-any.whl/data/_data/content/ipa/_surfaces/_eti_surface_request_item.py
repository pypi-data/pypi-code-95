# coding: utf8

from ._surface_request_item import SurfaceRequestItem
from ._enums import UnderlyingType
from ._eti_surface_definition import EtiSurfaceDefinition
from ._eti_surface_parameters import EtiSurfaceParameters as EtiCalculationParams


class EtiSurfaceRequestItem(SurfaceRequestItem):
    def __init__(
        self,
        surface_layout,
        surface_parameters,
        underlying_definition,
        surface_tag,
    ):
        super().__init__(
            surface_layout=surface_layout,
            surface_tag=surface_tag,
            underlying_type=UnderlyingType.ETI,
        )
        self.surface_parameters = surface_parameters
        self.underlying_definition = underlying_definition

    @property
    def surface_parameters(self):
        """
        The section that contains the properties that define how the volatility surface is generated
        :return: object EtiCalculationParams
        """
        return self._get_object_parameter(EtiCalculationParams, "surfaceParameters")

    @surface_parameters.setter
    def surface_parameters(self, value):
        self._set_object_parameter(EtiCalculationParams, "surfaceParameters", value)

    @property
    def underlying_definition(self):
        """
        The section that contains the properties that define the underlying instrument
        :return: object EtiSurfaceDefinition
        """
        return self._get_object_parameter(EtiSurfaceDefinition, "underlyingDefinition")

    @underlying_definition.setter
    def underlying_definition(self, value):
        self._set_object_parameter(EtiSurfaceDefinition, "underlyingDefinition", value)
