# coding: utf8

__all__ = ["FxUnderlyingDefinition"]

from typing import Optional

from .._base import UnderlyingDefinition


class FxUnderlyingDefinition(UnderlyingDefinition):
    """
    Parameters
    ----------
    fx_cross_code : str, optional
        The currency pair. Should contain the two currencies, ex EURUSD
    """

    def __init__(
        self,
        fx_cross_code: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.fx_cross_code = fx_cross_code

    @property
    def fx_cross_code(self):
        """
        The currency pair. Should contain the two currencies, ex EURUSD
        :return: str
        """
        return self._get_parameter("fxCrossCode")

    @fx_cross_code.setter
    def fx_cross_code(self, value):
        self._set_parameter("fxCrossCode", value)
