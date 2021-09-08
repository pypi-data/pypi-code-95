class LimitValue:
    """
    涨跌停限制
    """
    def __init__(self):
        self._up_limit = 0.1
        self._low_limit = 0.1

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
    def low_limit(self):
        """

        :return:
        """
        return self._low_limit

    @low_limit.setter
    def low_limit(self, value):
        self._low_limit = value
