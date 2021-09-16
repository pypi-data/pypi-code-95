# coding: utf8

__all__ = ["MoneynessWeight"]

from ..._object_definition import ObjectDefinition


class MoneynessWeight(ObjectDefinition):
    def __init__(self, max_moneyness=None, min_moneyness=None, weight=None):
        super().__init__()
        self.max_moneyness = max_moneyness
        self.min_moneyness = min_moneyness
        self.weight = weight

    @property
    def max_moneyness(self):
        """
        :return: float
        """
        return self._get_parameter("maxMoneyness")

    @max_moneyness.setter
    def max_moneyness(self, value):
        self._set_parameter("maxMoneyness", value)

    @property
    def min_moneyness(self):
        """
        :return: float
        """
        return self._get_parameter("minMoneyness")

    @min_moneyness.setter
    def min_moneyness(self, value):
        self._set_parameter("minMoneyness", value)

    @property
    def weight(self):
        """
        :return: float
        """
        return self._get_parameter("weight")

    @weight.setter
    def weight(self, value):
        self._set_parameter("weight", value)
