from SapphireQuant.Config.TradingFrame.TradingFrameHelper import TradingFrameHelper


class TradingFrameNode:
    def __init__(self):
        self._begin_day_string = ""
        self._trading_time = ""

    @property
    def begin_day_string(self):
        """

        :return:
        """
        return self._begin_day_string

    @begin_day_string.setter
    def begin_day_string(self, value):
        self._begin_day_string = value

    @property
    def trading_time(self):
        """

        :return:
        """
        return self._trading_time

    @trading_time.setter
    def trading_time(self, value):
        self._trading_time = value

    @property
    def begin_day(self):
        """

        :return:
        """
        return TradingFrameHelper.parse_date(self._begin_day_string)

    @property
    def trading_time_slices(self):
        """

        :return:
        """
        return TradingFrameHelper.parse_time_slice(self._trading_time)
