# Author     : lin le
# CreateTime : 2021/8/31 16:20
# Email      : linle861021@163.com

import time


class SimpleProcessbar:
    '''
    打印进度条
    '''

    def __init__(self, array_length: int, bar_length: int = 50):
        '''
        初始化
        :param array_length: 序列的长度
        :type array_length: int
        :param bar_length: 进度条的长度
        :type bar_length: int
        '''
        self.bar_length = bar_length
        self.array_length = array_length
        self.index_width = self.array_length / self.bar_length  # 进度条里的每一个字符代表index的宽度
        self.array_length_width = len(self.array_length.__str__())  # 序列总长度的字符数量
        self.starttime = time.perf_counter()  # 开始计时位置
        self.preindex = 0  # 上一次index的位置

    def __enter__(self):
        '''
        使用with实例化类时的入口
        例如：
            with SimpleProgressbar(10) as bar:  # 此时调用__enter__()
                pass
        '''
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        '''
        使用with类实例化类时，结束时自动调用
        例如：
            with SimpleProgressbar(10) as bar:
                pass
            # 在with结束时调用__exit__()
        '''
        self.close()

    def step(self, current_index: int, current_str: str = '>', remain_str: str = '.') -> None:
        '''
        打印进度
        打印条件设置：
            1、当前进度为0时打印
            2、当前进度为序列结尾索引是打印
            3、当前进度与上一次step时的进度相差一个字符代表的索引宽度时打印，防止打印频繁引起性能消耗过多
                self.preindex + self.index_width < current_index
        :param current_index: 当前序列位置
        :type current_index:int
        :param current_str:当前序列的字符
        :type current_str:str
        :param remain_str:剩余序列的字符
        :type remain_str:str
        :return: None
        :rtype: None
        '''

        if self.preindex + self.index_width < current_index or current_index == self.array_length - 1 or self.preindex == 0:
            percent = (current_index + 1) / self.array_length  # 当前进度百分比
            current_length = round((current_index + 1) / self.index_width)  # 进度条里已执行的长度
            remain_length = round((self.array_length - current_index - 1) / self.index_width)  # 进度条里未执行的长度
            time_interval = time.perf_counter() - self.starttime  # 执行时间
            print(f'\r|{current_str * current_length}{remain_str * remain_length}|',  # 进度条
                  f'{current_index + 1:{self.array_length_width}}/{self.array_length}',
                  # 数字进度，current_index/totle_index格式
                  f'[{percent * 100:6.2f}%]',  # 进度百分比，[百分比]格式
                  f'in {time_interval:.2f}s',  # 耗时
                  end='')
            self.preindex = current_index

    def close(self):
        print()
