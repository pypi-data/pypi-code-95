"""
BarBlock
"""


class DataBlock:
    """
    数据块，用于加快播放，根据current_index向下播放
    """

    def __init__(self, data_list):
        self.data_list = data_list
        self.current_index = -1

    def get_current_data(self):
        """
        获取当前data
        :return:
        """
        if len(self.data_list) > 0 and self.current_index < len(self.data_list):
            return self.data_list[self.current_index]

        return None
