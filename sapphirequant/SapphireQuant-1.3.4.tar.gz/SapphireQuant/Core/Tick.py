import time

from SapphireQuant.Core.Quote import Quote


class Tick:
    """
    Tick数据
    """

    def __init__(self):
        self._instrument_id = ""
        self._exchange_id = ""
        self._quote = Quote()
        self._last_price = 0.0
        self._iopv = 0.0
        self._pre_close_price = 0.0
        self._open_price = 0.0
        self._high_price = 0.0
        self._low_price = 0.0
        self._volume = 0
        self._turnover = 0.0
        self._up_limit_price = 0.0
        self._drop_limit_price = 0.0
        self._trading_date = time.time()
        self._natural_time = time.time()
        self._local_time = time.time()
        self._open_interest = 0.0
        self._pre_open_interest = 0.0
        self._pre_settlement_price = 0.0
        self._market = 1
        self._status = 1
        self.bid_price_level = 1
        self.ask_price_level = 1

        self.num_trades = 0
        self.total_bid_qty = 0
        self.total_ask_qty = 0
        self.weighted_avg_bid_price = 0.0
        self.weighted_avg_ask_price = 0.0

    @property
    def instrument_id(self):
        """

        :return:
        """
        return self._instrument_id

    @instrument_id.setter
    def instrument_id(self, value):
        self._instrument_id = value

    @property
    def exchange_id(self):
        """

        :return:
        """
        return self._exchange_id

    @exchange_id.setter
    def exchange_id(self, value):
        self._exchange_id = value

    @property
    def market(self):
        """

        :return:
        """
        return self._market

    @market.setter
    def market(self, value):
        self._market = value

    @property
    def local_time(self):
        """

        :return:
        """
        return self._local_time

    @local_time.setter
    def local_time(self, value):
        self._local_time = value

    @property
    def date_time(self):
        """

        :return:
        """
        return self._natural_time

    @date_time.setter
    def date_time(self, value):
        self._natural_time = value

    @property
    def time_now(self):
        """

        :return:
        """
        return time.mktime(str(self._natural_time.timetuple()))

    @property
    def trading_date(self):
        """

        :return:
        """
        return self._trading_date

    @trading_date.setter
    def trading_date(self, value):
        self._trading_date = value

    @property
    def quote(self):
        """

        :return:
        """
        return self._quote

    @quote.setter
    def quote(self, value):
        self._quote = value

    @property
    def ask_price1(self):
        """

        :return:
        """
        return self._quote.ask_price1

    @ask_price1.setter
    def ask_price1(self, value):
        self._quote.ask_price1 = value

    @property
    def ask_volume1(self):
        """

        :return:
        """
        return self._quote.ask_volume1

    @ask_volume1.setter
    def ask_volume1(self, value):
        self._quote.ask_volume1 = value

    @property
    def bid_price1(self):
        """

        :return:
        """
        return self._quote.bid_price1

    @bid_price1.setter
    def bid_price1(self, value):
        self._quote.bid_price1 = value

    @property
    def bid_volume1(self):
        """

        :return:
        """
        return self._quote.bid_volume1

    @bid_volume1.setter
    def bid_volume1(self, value):
        self._quote.bid_volume1 = value

    @property
    def pre_close_price(self):
        """

        :return:
        """
        return self._pre_close_price

    @pre_close_price.setter
    def pre_close_price(self, value):
        self._pre_close_price = value

    @property
    def open_price(self):
        """

        :return:
        """
        return self._open_price

    @open_price.setter
    def open_price(self, value):
        self._open_price = value

    @property
    def high_price(self):
        """

        :return:
        """
        return self._high_price

    @high_price.setter
    def high_price(self, value):
        self._high_price = value

    @property
    def low_price(self):
        """

        :return:
        """
        return self._low_price

    @low_price.setter
    def low_price(self, value):
        self._low_price = value

    @property
    def last_price(self):
        """

        :return:
        """
        return self._last_price

    @last_price.setter
    def last_price(self, value):
        self._last_price = value

    @property
    def iopv(self):
        """

        :return:
        """
        return self._iopv

    @iopv.setter
    def iopv(self, value):
        self._iopv = value

    @property
    def volume(self):
        """

        :return:
        """
        return self._volume

    @volume.setter
    def volume(self, value):
        self._volume = value

    @property
    def turnover(self):
        """

        :return:
        """
        return self._turnover

    @turnover.setter
    def turnover(self, value):
        self._turnover = value

    @property
    def up_limit(self):
        """

        :return:
        """
        return self._up_limit_price

    @up_limit.setter
    def up_limit(self, value):
        self._up_limit_price = value

    @property
    def drop_limit(self):
        """

        :return:
        """
        return self._drop_limit_price

    @drop_limit.setter
    def drop_limit(self, value):
        self._drop_limit_price = value

    @property
    def open_interest(self):
        """

        :return:
        """
        return self._open_interest

    @open_interest.setter
    def open_interest(self, value):
        self._open_interest = value

    @property
    def pre_open_interest(self):
        """

        :return:
        """
        return self._pre_open_interest

    @pre_open_interest.setter
    def pre_open_interest(self, value):
        self._pre_open_interest = value

    @property
    def pre_settlement_price(self):
        """

        :return:
        """
        return self._pre_settlement_price

    @pre_settlement_price.setter
    def pre_settlement_price(self, value):
        self._pre_settlement_price = value

    @property
    def change(self):
        """

        :return:
        """
        if self.pre_close_price > 0.0:
            return round((self.last_price / self.pre_close_price - 1.0) * 100.0, 4)
        if self.pre_settlement_price > 0.0:
            return round((self.last_price / self.pre_settlement_price - 1.0) * 100.0, 4)
        return 0.0

    @property
    def if_up_limit(self):
        """

        :return:
        """
        return (self.ask_price1 <= 0.0) & (self.bid_price1 > 0.0)

    @property
    def IfDropLimit(self):
        """

        :return:
        """
        return (self.bid_price1 <= 0.0) & (self.ask_price1 > 0.0)

    @property
    def status(self):
        """

        :return:
        """
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @property
    def bid_num_order1(self):
        """

        :return:
        """
        return self.quote.bid_num_order1

    @property
    def ask_num_order1(self):
        """

        :return:
        """
        return self.quote.ask_num_order1

    def to_string(self):
        """
        转换为string
        :return:
        """
        string_builder = ''
        string_builder += str(self.market)
        string_builder += ("[" + self.instrument_id + "]")
        string_builder += ("交易日" + self.trading_date.strftime('%Y/%m/%d')) + ","
        string_builder += ("自然时" + self.date_time.strftime('%Y/%m/%d %H:%M:%S.%f')) + ","
        string_builder += ("最新=" + str(self.last_price)) + ","
        string_builder += ("开=" + str(self.open_price)) + ","
        string_builder += ("高=" + str(self.high_price)) + ","
        string_builder += ("低=" + str(self.low_price)) + ","
        string_builder += ("昨收=" + str(self.pre_close_price)) + ","
        if self.change >= 0.0:
            string_builder += ("涨幅=" + str(round(self.change, 2))) + "%,"
        else:
            string_builder += ("跌幅=" + str(round(self.change, 2))) + "%,"
        string_builder += ("量" + str(self.volume)) + ","
        string_builder += ("额" + str(self.turnover)) + ","
        string_builder += ("[" + str(self.quote.bid_volume1) + "|" + str(self.quote.bid_price1) + "][" + str(self.quote.ask_price1) + "|" +
                           str(self.quote.ask_volume1) + "]")
        return string_builder

    def clone(self):
        """
        克隆
        :return:
        """
        tick = Tick()
        tick._market = self._market
        tick._natural_time = self._natural_time
        tick._trading_date = self._trading_date
        tick._drop_limit_price = self._drop_limit_price
        tick._exchangeId = self._exchange_id
        tick._highPrice = self._high_price
        tick._instrument_id = self._instrument_id
        tick._last_price = self._last_price
        tick._low_price = self._low_price
        tick._open_interest = self._open_interest
        tick._open_price = self._open_price
        tick._pre_close_price = self._pre_close_price
        tick._pre_open_interest = self._pre_open_interest
        tick._pre_settlement_price = self._pre_settlement_price

        if self._quote is not None:
            tick._quote = self._quote.clone()

        tick._turnover = self._turnover
        tick._up_limit_price = self._up_limit_price
        tick._volume = self._volume

        return tick
