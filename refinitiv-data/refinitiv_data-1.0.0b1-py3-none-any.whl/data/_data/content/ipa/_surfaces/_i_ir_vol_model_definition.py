# coding: utf8


from .._object_definition import ObjectDefinition
from ._enums import DiscountingType


class IIrVolModelDefinition(ObjectDefinition):
    def __init__(self, instrument_code=None, discounting_type=None):
        super().__init__()
        self.instrument_code = instrument_code
        self.discounting_type = discounting_type

    @property
    def discounting_type(self):
        """
        the discounting type of the IR vol model: OisDiscounting, or BorDiscounting (default)
        :return: enum DiscountingType
        """
        return self._get_enum_parameter(DiscountingType, "discountingType")

    @discounting_type.setter
    def discounting_type(self, value):
        self._set_enum_parameter(DiscountingType, "discountingType", value)

    @property
    def instrument_code(self):
        """
        The currency of the stripped cap surface, vol cube, or interest rate vol model
        :return: str
        """
        return self._get_parameter("instrumentCode")

    @instrument_code.setter
    def instrument_code(self, value):
        self._set_parameter("instrumentCode", value)
