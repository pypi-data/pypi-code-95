# coding: utf8

__all__ = ["BidAskMid"]

from typing import Optional

from .._object_definition import ObjectDefinition


class BidAskMid(ObjectDefinition):
    """
    Parameters
    ----------
    bid : float, optional

    ask : float, optional

    mid : float, optional

    """

    def __init__(
        self,
        bid: Optional[float] = None,
        ask: Optional[float] = None,
        mid: Optional[float] = None,
    ) -> None:
        super().__init__()
        self.bid = bid
        self.ask = ask
        self.mid = mid

    @property
    def ask(self):
        """
        :return: float
        """
        return self._get_parameter("ask")

    @ask.setter
    def ask(self, value):
        self._set_parameter("ask", value)

    @property
    def bid(self):
        """
        :return: float
        """
        return self._get_parameter("bid")

    @bid.setter
    def bid(self, value):
        self._set_parameter("bid", value)

    @property
    def mid(self):
        """
        :return: float
        """
        return self._get_parameter("mid")

    @mid.setter
    def mid(self, value):
        self._set_parameter("mid", value)
