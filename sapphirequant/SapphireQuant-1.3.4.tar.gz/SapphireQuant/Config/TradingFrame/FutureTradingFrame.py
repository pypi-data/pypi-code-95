class FutureTradingFrame:
    """
    期货交易时间框架
    """
    def __init__(self):
        self._exchanges = []

    @property
    def exchanges(self):
        """

        :return:
        """
        return self._exchanges

    @exchanges.setter
    def exchanges(self, value):
        self._exchanges = value
