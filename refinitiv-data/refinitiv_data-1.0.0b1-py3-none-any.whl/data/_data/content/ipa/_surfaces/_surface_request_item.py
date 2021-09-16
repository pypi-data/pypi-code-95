# coding: utf8

from ._enums import UnderlyingType
from ._models import SurfaceOutput as SurfaceLayout
from .._object_definition import ObjectDefinition


class SurfaceRequestItem(ObjectDefinition):
    def __init__(
        self,
        surface_layout,
        surface_tag,
        underlying_type,
    ):
        super().__init__()
        self.surface_tag = surface_tag
        self.surface_layout = surface_layout
        self.underlying_type = underlying_type

    @property
    def surface_layout(self):
        """
        The section that contains the properties that define how the volatility surface is returned
        :return: object SurfaceLayout
        """
        return self._get_object_parameter(SurfaceLayout, "surfaceLayout")

    @surface_layout.setter
    def surface_layout(self, value):
        self._set_object_parameter(SurfaceLayout, "surfaceLayout", value)

    @property
    def underlying_type(self):
        """
        The type of the underlying used to generate the volatility surface
        :return: enum UnderlyingType
        """
        return self._get_enum_parameter(UnderlyingType, "underlyingType")

    @underlying_type.setter
    def underlying_type(self, value):
        self._set_enum_parameter(UnderlyingType, "underlyingType", value)

    @property
    def surface_tag(self):
        """
        A user defined string to describe the volatility surface
        :return: str
        """
        return self._get_parameter("surfaceTag")

    @surface_tag.setter
    def surface_tag(self, value):
        self._set_parameter("surfaceTag", value)
