from SapphireQuant.Config.TradingFrame.LimitValue import LimitValue


class FutureProductTradingFrame:
    """
    产品TradingFrame
    """
    def __init__(self):
        self._id = ""
        self._name = ""
        self._trading_frames = []
        self._limit_value = LimitValue()

    @property
    def id(self):
        """

        :return:
        """
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def name(self):
        """

        :return:
        """
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def trading_frames(self):
        """

        :return:
        """
        return self._trading_frames

    @trading_frames.setter
    def trading_frames(self, value):
        self._trading_frames = value

    @property
    def limit_value(self):
        """

        :return:
        """
        return self._limit_value

    @limit_value.setter
    def limit_value(self, value):
        self._limit_value = value
