from SapphireQuant.Core.Enum import EnumProductClass
from SapphireQuant.Core.Enum.EnumLifePhase import EnumLifePhase
from SapphireQuant.Core.Enum.EnumMarket import EnumMarket
from SapphireQuant.Core.Tick import Tick


class Instrument:
    """
    合约
    """
    def __init__(self):
        self._id = ""
        self._can_sel_today_pos = True
        self._market = EnumMarket.期货
        self._exchange_id = "SHFE"
        self._name = ""
        self._last_tick = Tick()
        self._last_price = 0.0
        self._pre_close = 0.0
        self._pre_settlement_price = 0.0
        self._up_limit = 0.0
        self._drop_limit = 0.0
        self._volume_multiple = 1
        self._price_tick = 0.01
        self._life_phase = EnumLifePhase.上市
        self._up_limit_ratio = 0.0
        self._drop_limit_ratio = 0.0
        self._lot_size = 0
        self._product_id = ""
        self.product_class = EnumProductClass.future

        self._tick_event = None

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
    def can_sel_today_pos(self):
        """

        :return:
        """
        return self._can_sel_today_pos

    @can_sel_today_pos.setter
    def can_sel_today_pos(self, value):
        self._can_sel_today_pos = value

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
    def exchange_id(self):
        """

        :return:
        """
        return self._exchange_id

    @exchange_id.setter
    def exchange_id(self, value):
        self._exchange_id = value

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
    def last_tick(self):
        """

        :return:
        """
        return self._last_tick

    @last_tick.setter
    def last_tick(self, value):
        self._last_tick = value

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
    def pre_close(self):
        """

        :return:
        """
        return self._pre_close

    @pre_close.setter
    def pre_close(self, value):
        self._pre_close = value

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
    def up_limit(self):
        """

        :return:
        """
        return self._up_limit

    @up_limit.setter
    def up_limit(self, value):
        self._up_limit = value

    @property
    def rop_limit(self):
        """

        :return:
        """
        return self._drop_limit

    @rop_limit.setter
    def rop_limit(self, value):
        self._drop_limit = value

    @property
    def volume_multiple(self):
        """

        :return:
        """
        return self._volume_multiple

    @volume_multiple.setter
    def volume_multiple(self, value):
        self._volume_multiple = value

    @property
    def price_tick(self):
        """

        :return:
        """
        return self._price_tick

    @price_tick.setter
    def price_tick(self, value):
        self._price_tick = value

    @property
    def life_phase(self):
        """

        :return:
        """
        return self._life_phase

    @life_phase.setter
    def life_phase(self, value):
        self._life_phase = value

    @property
    def up_limit_ratio(self):
        """

        :return:
        """
        return self._up_limit_ratio

    @up_limit_ratio.setter
    def up_limit_ratio(self, value):
        self._up_limit_ratio = value

    @property
    def drop_limit_ratio(self):
        """

        :return:
        """
        return self._drop_limit_ratio

    @drop_limit_ratio.setter
    def drop_limit_ratio(self, value):
        self._drop_limit_ratio = value

    @property
    def lot_size(self):
        """

        :return:
        """
        return self._lot_size

    @lot_size.setter
    def lot_size(self, value):
        self._lot_size = value

    @property
    def product_id(self):
        """

        :return:
        """
        return self._product_id

    @product_id.setter
    def product_id(self, value):
        self._product_id = value

    def on_tick(self, tick):
        """

        :param tick:
        """
        if tick is not None:
            tick.ExchangeId = self._exchange_id
            self._last_tick = tick
            if self._tick_event is not None:
                try:
                    self._tick_event(tick)
                except Exception as e:
                    print(str(e))

    def to_string(self):
        """

        :return:
        """
        string_builder = ""
        string_builder += ("[" + self._id + "]")
        string_builder += self._name + ","
        string_builder += self._exchange_id + ","
        string_builder += "PriceTick=" + str(self._price_tick) + ","
        string_builder += "VolumeMultiple=" + str(self._volume_multiple) + ","
        string_builder += "昨收=" + str(self._pre_close) + ","
        return string_builder
