# coding: utf8

__all__ = ["EtiCbbcDefinition"]

from typing import Optional

from ...instrument._instrument_definition import ObjectDefinition


class EtiCbbcDefinition(ObjectDefinition):
    """
    Parameters
    ----------
    conversion_ratio : float, optional

    level : float, optional

    """

    def __init__(
        self,
        conversion_ratio: Optional[float] = None,
        level: Optional[float] = None,
    ) -> None:
        super().__init__()
        self.conversion_ratio = conversion_ratio
        self.level = level

    @property
    def conversion_ratio(self):
        """
        :return: float
        """
        return self._get_parameter("conversionRatio")

    @conversion_ratio.setter
    def conversion_ratio(self, value):
        self._set_parameter("conversionRatio", value)

    @property
    def level(self):
        """
        :return: float
        """
        return self._get_parameter("level")

    @level.setter
    def level(self, value):
        self._set_parameter("level", value)
