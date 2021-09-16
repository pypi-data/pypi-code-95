# coding: utf8

__all__ = ["EtiUnderlyingDefinition"]

from typing import Optional

from .._base import UnderlyingDefinition


class EtiUnderlyingDefinition(UnderlyingDefinition):
    """
    Parameters
    ----------
    instrument_code : str, optional
        The underlier RIC
    """

    def __init__(
        self,
        instrument_code: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.instrument_code = instrument_code

    @property
    def instrument_code(self):
        """
        The underlier RIC
        :return: str
        """
        return self._get_parameter("instrumentCode")

    @instrument_code.setter
    def instrument_code(self, value):
        self._set_parameter("instrumentCode", value)
