# coding: utf8

__all__ = ["PayoutScaling"]

from typing import Optional

from .._object_definition import ObjectDefinition


class PayoutScaling(ObjectDefinition):
    """
    Parameters
    ----------
    maximum : float, optional

    minimum : float, optional

    """

    def __init__(
        self,
        maximum: Optional[float] = None,
        minimum: Optional[float] = None,
    ) -> None:
        super().__init__()
        self.maximum = maximum
        self.minimum = minimum

    @property
    def maximum(self):
        """
        :return: float
        """
        return self._get_parameter("maximum")

    @maximum.setter
    def maximum(self, value):
        self._set_parameter("maximum", value)

    @property
    def minimum(self):
        """
        :return: float
        """
        return self._get_parameter("minimum")

    @minimum.setter
    def minimum(self, value):
        self._set_parameter("minimum", value)
