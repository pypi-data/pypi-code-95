# coding: utf8

from ._surface_request_item import SurfaceRequestItem

from ._enums import UnderlyingType
from ._fx_surface_parameters import FxSurfaceParameters as FxCalculationParams
from ._fx_surface_definition import FxVolatilitySurfaceDefinition as FxSurfaceDefinition


class FxSurfaceRequestItem(SurfaceRequestItem):
    def __init__(
        self,
        surface_layout=None,
        surface_parameters=None,
        underlying_definition=None,
        surface_tag=None,
    ):
        super().__init__(
            surface_layout=surface_layout,
            surface_tag=surface_tag,
            underlying_type=UnderlyingType.FX,
        )
        self.surface_parameters = surface_parameters
        self.underlying_definition = underlying_definition

    @property
    def surface_parameters(self):
        """
        The section that contains the properties that define how the volatility surface is generated
        :return: object FxCalculationParams
        """
        return self._get_object_parameter(FxCalculationParams, "surfaceParameters")

    @surface_parameters.setter
    def surface_parameters(self, value):
        self._set_object_parameter(FxCalculationParams, "surfaceParameters", value)

    @property
    def underlying_definition(self):
        """
        The section that contains the properties that define the underlying instrument
        :return: object FxSurfaceDefinition
        """
        return self._get_object_parameter(FxSurfaceDefinition, "underlyingDefinition")

    @underlying_definition.setter
    def underlying_definition(self, value):
        self._set_object_parameter(FxSurfaceDefinition, "underlyingDefinition", value)
