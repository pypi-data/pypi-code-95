from datetime import datetime


class Holiday:
    """
    节假日信息
    """
    def __init__(self):
        self.name = ''
        self.pre_holiday_trading_date = datetime.min
        self.begin_date = datetime.min
        self.end_date = datetime.min
        self.post_holiday_trading_date = datetime.min

    def to_string(self):
        """

        :return:
        """
        return '{0}:[{1}-{2}],假期前最后一个交易日:{3}.假期后第一个交易日:{4}'.format(self.name,
                                                                   self.begin_date.strftime('%Y%m%d'), self.end_date.strftime('%Y%m%d'),
                                                                   self.pre_holiday_trading_date.strftime('%Y%m%d'), self.post_holiday_trading_date.strftime('%Y%m%d'))
