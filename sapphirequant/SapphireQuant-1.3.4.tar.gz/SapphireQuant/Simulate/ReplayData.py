from SapphireQuant.Simulate.DataBlock import DataBlock


class ReplayData:
    """
    播放数据
    """
    def __init__(self, instrument_id):
        self.instrument_id = instrument_id
        self.data_block_map = {}
        self.current_trading_date = None

    def clear(self, trading_date):
        """
        清空指定交易日的缓存
        :param trading_date:
        """
        if trading_date in self.data_block_map.keys():
            tb = self.data_block_map[trading_date]
            tb.data_list.clear()

    def add_data(self, trading_date, data_list):
        """
        添加数据
        :param trading_date:
        :param data_list:
        """
        if trading_date not in self.data_block_map.keys():
            self.data_block_map[trading_date] = DataBlock(data_list)

    def replay_bar_to_time(self, end_time):
        """
        播放到时间
        :param end_time:
        :return:
        """
        if self.current_trading_date not in self.data_block_map.keys():
            return False, []
        tb = self.data_block_map[self.current_trading_date]
        if len(tb.data_list) <= 0:
            return False, []

        i = tb.current_index + 1
        wait_play_bars = []
        while i < len(tb.data_list):
            data = tb.data_list[i]
            if data.end_time <= end_time:
                wait_play_bars.append(data)
            else:
                break
            i += 1

        tb.current_index = i - 1

        if tb.current_index < 0:
            return False, []

        if tb.data_list[i-1].end_time <= end_time:
            return True, wait_play_bars

        return False, []

    def replay_tick_to_time(self, end_time):
        """
        播放到时间
        :param end_time:
        :return:
        """
        if self.current_trading_date not in self.data_block_map.keys():
            return False, []
        tb = self.data_block_map[self.current_trading_date]
        if len(tb.data_list) <= 0:
            return False, []

        i = tb.current_index + 1
        wait_play_ticks = []
        while i < len(tb.data_list):
            data = tb.data_list[i]
            if data.date_time <= end_time:
                wait_play_ticks.append(data)
            else:
                break
            i += 1

        tb.current_index = i - 1

        if tb.current_index < 0:
            return False, []

        if tb.data_list[i-1].date_time <= end_time:
            return True, wait_play_ticks

        return False, []
