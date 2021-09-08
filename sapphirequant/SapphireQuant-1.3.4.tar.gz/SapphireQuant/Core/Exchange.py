import datetime

from SapphireQuant.Core.Enum.EnumExchange import EnumExchange


class Exchange:
    """
    交易市场
    """
    def __init__(self):
        self._exchange_id = ""
        self._exchange_name = ""
        self._close_time = None
        self._open_time = None

        self._base_time = None
        self._diff_time = None
        self._all_slice = []

    @property
    def exchange_id(self):
        return self._exchange_id

    @exchange_id.setter
    def exchange_id(self, value):
        self._exchange_id = value

    @property
    def exchange_name(self):
        return self._exchange_name

    @exchange_name.setter
    def exchange_name(self, value):
        self._exchange_name = value

    @property
    def close_time(self):
        return self._close_time

    @close_time.setter
    def close_time(self, value):
        self._close_time = value

    @property
    def open_time(self):
        return self._open_time

    @open_time.setter
    def open_time(self, value):
        self._open_time = value

    @property
    def time_now(self):
        if self._base_time == datetime.datetime:
            return datetime.datetime.now() + self._diff_time
        return self._base_time

    @property
    def base_time(self):
        return self._base_time

    @base_time.setter
    def base_time(self, value):
        self._base_time = value

    @property
    def diff_time(self):
        return self._diff_time

    @diff_time.setter
    def diff_time(self, value):
        self._diff_time = value

    @property
    def all_slice(self):
        return self._all_slice

    @all_slice.setter
    def all_slice(self, value):
        self._all_slice = value

    @property
    def exchange_enum(self):
        if self._exchange_id == "CFFE":
            return EnumExchange.中金所
        elif self._exchange_id == "DCE":
            return EnumExchange.大商所
        elif self._exchange_id == "SHFE":
            return EnumExchange.上期所
        elif self._exchange_id == "CZCE":
            return EnumExchange.郑商所
        elif self._exchange_id == "SH":
            return EnumExchange.上证所
        elif self._exchange_id == "SZ":
            return EnumExchange.深交所
        return EnumExchange.未知

    def to_string(self):
        pass
