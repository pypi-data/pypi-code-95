# coding: utf8

__all__ = ["PdeParameters"]

from .._object_definition import ObjectDefinition


class PdeParameters(ObjectDefinition):
    def __init__(
        self,
        pde_space_step_number=None,
        pde_standard_deviation=None,
        pde_time_step_number=None,
    ):
        super().__init__()
        self.pde_space_step_number = pde_space_step_number
        self.pde_standard_deviation = pde_standard_deviation
        self.pde_time_step_number = pde_time_step_number

    @property
    def pde_space_step_number(self):
        """
        :return: int
        """
        return self._get_parameter("pdeSpaceStepNumber")

    @pde_space_step_number.setter
    def pde_space_step_number(self, value):
        self._set_parameter("pdeSpaceStepNumber", value)

    @property
    def pde_standard_deviation(self):
        """
        :return: int
        """
        return self._get_parameter("pdeStandardDeviation")

    @pde_standard_deviation.setter
    def pde_standard_deviation(self, value):
        self._set_parameter("pdeStandardDeviation", value)

    @property
    def pde_time_step_number(self):
        """
        :return: int
        """
        return self._get_parameter("pdeTimeStepNumber")

    @pde_time_step_number.setter
    def pde_time_step_number(self, value):
        self._set_parameter("pdeTimeStepNumber", value)
