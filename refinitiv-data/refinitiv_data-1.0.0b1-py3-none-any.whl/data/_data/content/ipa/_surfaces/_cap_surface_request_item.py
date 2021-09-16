# coding: utf8


from ._surface_request_item import SurfaceRequestItem
from ._enums import UnderlyingType
from ._i_ir_vol_model_definition import IIrVolModelDefinition as CapSurfaceDefinition
from ._i_ir_vol_model_pricing_parameters import (
    IIrVolModelPricingParameters as CapCalculationParams,
)


class CapSurfaceRequestItem(SurfaceRequestItem):
    def __init__(
        self,
        instrument_type,
        surface_layout,
        surface_params,
        underlying_definition,
        surface_tag,
    ):
        super().__init__(
            surface_layout=surface_layout,
            surface_tag=surface_tag,
            underlying_type=UnderlyingType.CAP,
        )
        self.instrument_type = instrument_type
        self.surface_parameters = surface_params
        self.underlying_definition = underlying_definition

    @property
    def surface_parameters(self):
        """
        :return: object CapCalculationParams
        """
        return self._get_object_parameter(CapCalculationParams, "surfaceParameters")

    @surface_parameters.setter
    def surface_parameters(self, value):
        self._set_object_parameter(CapCalculationParams, "surfaceParameters", value)

    @property
    def underlying_definition(self):
        """
        :return: object CapSurfaceDefinition
        """
        return self._get_object_parameter(CapSurfaceDefinition, "underlyingDefinition")

    @underlying_definition.setter
    def underlying_definition(self, value):
        self._set_object_parameter(CapSurfaceDefinition, "underlyingDefinition", value)

    @property
    def instrument_type(self):
        """
        The type of instrument being defined.
        :return: str
        """
        return self._get_parameter("instrumentType")

    @instrument_type.setter
    def instrument_type(self, value):
        self._set_parameter("instrumentType", value)
