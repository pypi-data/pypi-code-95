import sys
import datetime


class CSharpUtils:
    """
    CSharp工具类
    """
    @staticmethod
    def convert_c_sharp_ticks_to_linux_ticks(value):
        """
        将CSharp Ticks转换成Linux Ticks
        :param value:
        :return:
        """
        if value == 0:
            return value
        c_sharp_ticks1970 = 621355968000000000
        linux_ticks = (value - c_sharp_ticks1970) / 10000000
        time_zone = 28800
        linux_ticks = linux_ticks - time_zone
        return linux_ticks

    @staticmethod
    def convert_c_sharp_ticks_to_py_date_time(value):
        """
        将CSharp Ticks转换成python datetime
        :param value:
        :return:
        """
        py_time = datetime.datetime.fromtimestamp(CSharpUtils.convert_c_sharp_ticks_to_linux_ticks(value))
        return py_time

    @staticmethod
    def get_c_sharp_ticks(value):
        """

        :param value:
        :return:
        """
        c_sharp_ticks1970 = 621355968000000000
        linux_ticks = value.timestamp()
        time_zone = 28800
        linux_ticks = linux_ticks + time_zone
        c_sharp_ticks = linux_ticks * 10000000 + c_sharp_ticks1970
        return int(c_sharp_ticks)
