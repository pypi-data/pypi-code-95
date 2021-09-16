# coding: utf8

__all__ = ["ConvexityAdjustment"]

from .._forward_curve_types import OptFloat
from ..._object_definition import ObjectDefinition


class ConvexityAdjustment(ObjectDefinition):
    """
    Parameters
    ----------
    mean_reversion_percent : float, optional
        Reversion speed rate, expressed in percents, used to calculate the convexity
        adjustment
    volatility_percent : float, optional
        Reversion flat volatility, expressed in percents, used to calculate the
        convexity adjustment
    """

    def __init__(
        self,
        mean_reversion_percent: OptFloat = None,
        volatility_percent: OptFloat = None,
    ) -> None:
        super().__init__()
        self.mean_reversion_percent = mean_reversion_percent
        self.volatility_percent = volatility_percent

    @property
    def mean_reversion_percent(self):
        """
        Reversion speed rate, expressed in percents, used to calculate the convexity
        adjustment
        :return: float
        """
        return self._get_parameter("meanReversionPercent")

    @mean_reversion_percent.setter
    def mean_reversion_percent(self, value):
        self._set_parameter("meanReversionPercent", value)

    @property
    def volatility_percent(self):
        """
        Reversion flat volatility, expressed in percents, used to calculate the
        convexity adjustment
        :return: float
        """
        return self._get_parameter("volatilityPercent")

    @volatility_percent.setter
    def volatility_percent(self, value):
        self._set_parameter("volatilityPercent", value)
