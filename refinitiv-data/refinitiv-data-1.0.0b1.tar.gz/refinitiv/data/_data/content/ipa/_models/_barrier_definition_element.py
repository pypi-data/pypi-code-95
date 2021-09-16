# coding: utf8

__all__ = ["BarrierDefinitionElement"]

from .._object_definition import ObjectDefinition
from .._enums import BarrierType


class BarrierDefinitionElement(ObjectDefinition):
    def __init__(
        self,
        barrier_type=None,
        barrier_down_percent=None,
        barrier_up_percent=None,
        rebate_down_percent=None,
        rebate_up_percent=None,
    ):
        super().__init__()
        self.barrier_type = barrier_type
        self.barrier_down_percent = barrier_down_percent
        self.barrier_up_percent = barrier_up_percent
        self.rebate_down_percent = rebate_down_percent
        self.rebate_up_percent = rebate_up_percent

    @property
    def barrier_type(self):
        """
        :return: enum BarrierType
        """
        return self._get_enum_parameter(BarrierType, "barrierType")

    @barrier_type.setter
    def barrier_type(self, value):
        self._set_enum_parameter(BarrierType, "barrierType", value)

    @property
    def barrier_down_percent(self):
        """
        :return: float
        """
        return self._get_parameter("barrierDownPercent")

    @barrier_down_percent.setter
    def barrier_down_percent(self, value):
        self._set_parameter("barrierDownPercent", value)

    @property
    def barrier_up_percent(self):
        """
        :return: float
        """
        return self._get_parameter("barrierUpPercent")

    @barrier_up_percent.setter
    def barrier_up_percent(self, value):
        self._set_parameter("barrierUpPercent", value)

    @property
    def rebate_down_percent(self):
        """
        :return: float
        """
        return self._get_parameter("rebateDownPercent")

    @rebate_down_percent.setter
    def rebate_down_percent(self, value):
        self._set_parameter("rebateDownPercent", value)

    @property
    def rebate_up_percent(self):
        """
        :return: float
        """
        return self._get_parameter("rebateUpPercent")

    @rebate_up_percent.setter
    def rebate_up_percent(self, value):
        self._set_parameter("rebateUpPercent", value)
