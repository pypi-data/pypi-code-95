# coding: utf8

from .._object_definition import ObjectDefinition


class EtiSurfaceDefinition(ObjectDefinition):
    def __init__(
        self,
        instrument_code=None,
        clean_instrument_code=None,
        exchange=None,
        is_future_underlying=None,
    ):
        super().__init__()
        self.instrument_code = instrument_code
        self.clean_instrument_code = clean_instrument_code
        self.exchange = exchange
        self.is_future_underlying = is_future_underlying

    @property
    def clean_instrument_code(self):
        """
        :return: str
        """
        return self._get_parameter("cleanInstrumentCode")

    @clean_instrument_code.setter
    def clean_instrument_code(self, value):
        self._set_parameter("cleanInstrumentCode", value)

    @property
    def exchange(self):
        """
        Specifies the exchange to be used to retrieve the underlying data.
        :return: str
        """
        return self._get_parameter("exchange")

    @exchange.setter
    def exchange(self, value):
        self._set_parameter("exchange", value)

    @property
    def instrument_code(self):
        """
        The code (RIC for equities and indices and RICROOT for Futures.) that represents the instrument.
        The format for equities and indices is xxx@RIC (Example: VOD.L@RIC)
        The format for Futures is xx@RICROOT (Example: CL@RICROOT)
        :return: str
        """
        return self._get_parameter("instrumentCode")

    @instrument_code.setter
    def instrument_code(self, value):
        self._set_parameter("instrumentCode", value)

    @property
    def is_future_underlying(self):
        """
        :return: bool
        """
        return self._get_parameter("isFutureUnderlying")

    @is_future_underlying.setter
    def is_future_underlying(self, value):
        self._set_parameter("isFutureUnderlying", value)
