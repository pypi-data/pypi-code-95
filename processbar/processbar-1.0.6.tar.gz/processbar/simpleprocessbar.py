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
        self.__bar_length = bar_length
        self.__array_length = array_length
        self.__index_width = self.__array_length / self.__bar_length  # 进度条里的每一个字符代表index的宽度
        self.__array_length_width = len(self.__array_length.__str__())  # 序列总长度的字符数量
        self.__starttime = time.perf_counter()  # 开始计时位置
        self.__preindex = 0  # 上一次index的位置

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

    def step(self, current_index: int, current_str: str = '>', remain_str: str = '.', zip_step: bool = False,
             step_info: str = None) -> None:
        '''
        打印进度
        :param current_index: 当前序列位置
        :param current_str:当前序列的字符
        :param remain_str:剩余序列的字符
        :param zip_step: 是否压缩step,防止打印频繁导致性能消耗过多
        :param step_info: 打印步骤具体内容
        :return: None
        :rtype: None
        '''
        if current_index == self.__array_length - 1 or current_index == 0:  # 第一个或最后一个索引，直接打印
            self.__print_step(current_index, current_str, remain_str, step_info)
        else:
            if zip_step:  # 如果需要压缩step
                if current_index - self.__preindex >= self.__index_width:  # 每隔一个字符代表的宽带，打印一次
                    self.__print_step(current_index, current_str, remain_str, step_info)
            else:
                self.__print_step(current_index, current_str, remain_str, step_info.__str__())  # 如果不需要压缩，则直接打印每个step

    def __print_step(self, current_index, current_str, remain_str, step_info):  # 打印进度条
        if current_index >= self.__array_length:
            raise IOError('当前进度大于序列总长度')
        self.real_current_index = current_index + 1
        percent = self.real_current_index / self.__array_length  # 当前进度百分比
        current_length = round(self.real_current_index / self.__index_width)  # 进度条里已执行的长度
        remain_length = round((self.__array_length - current_index - 1) / self.__index_width)  # 进度条里未执行的长度
        time_interval = time.perf_counter() - self.__starttime  # 执行时间
        print(f'\r|{current_str * current_length}{remain_str * remain_length}|',  # 进度条
              f'{self.real_current_index:{self.__array_length_width}}/{self.__array_length}',
              # 数字进度，current_index/totle_index格式
              f'[{percent * 100:6.2f}%]',  # 进度百分比，[百分比]格式
              f'in {time_interval:.2f}s',  # 耗时
              step_info,
              end='')
        self.__preindex = current_index

    def close(self):
        print()
