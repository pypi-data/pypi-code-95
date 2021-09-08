
import datetime

from SapphireQuant.Core.CSharpUtils import CSharpUtils
from SapphireQuant.Core.Enum.EnumBarType import EnumBarType
from SapphireQuant.Core.Enum.EnumMarket import EnumMarket
from SapphireQuant.DataProcessing.DateTimeOffsetMap import DateTimeOffsetMap


class FileHeader:
    """
    头文件
    """
    FileVersionSize = 8
    FileHeaderSize = 64
    FileHeaderTotalSize = 64 + 32 * 20 + 32 * 20

    def __init__(self):
        self._isDirty = False
        self._file_version = '1.0'
        self._market = EnumMarket.期货
        self._bar_type = EnumBarType.minute
        self._begin_time = datetime.datetime(2999, 1, 1)
        self._end_time = datetime.datetime(2999, 1, 1)
        self._begin_trading_day = datetime.datetime(2999, 1, 1)
        self._end_trading_day = datetime.datetime(2999, 1, 1)
        self._bar_count = 0
        self._period = 1
        self._trading_day_indices = DateTimeOffsetMap(self)
        self._natural_day_indices = DateTimeOffsetMap(self)

    @property
    def file_version(self):
        """
        文件版本
        :return:
        """
        return self._file_version

    @file_version.setter
    def file_version(self, value):
        self._file_version = value

    @property
    def market(self):
        """
        市场
        :return:
        """
        return self._market

    @market.setter
    def market(self, value):
        self._market = value

    @property
    def bar_type(self):
        """
        分钟线类型
        :return:
        """
        return self._bar_type

    @bar_type.setter
    def bar_type(self, value):
        self._bar_type = value

    @property
    def begin_time(self):
        """
        开始时间
        :return:
        """
        return self._begin_time

    @begin_time.setter
    def begin_time(self, value):
        self._begin_time = value

    @property
    def end_time(self):
        """
        截止时间
        :return:
        """
        return self._end_time

    @end_time.setter
    def end_time(self, value):
        self._end_time = value

    @property
    def begin_trading_day(self):
        """
        开始交易日
        :return:
        """
        return self._begin_trading_day

    @begin_trading_day.setter
    def begin_trading_day(self, value):
        self._begin_trading_day = value

    @property
    def end_trading_day(self):
        """
        结束交易日
        :return:
        """
        return self._end_trading_day

    @end_trading_day.setter
    def end_trading_day(self, value):
        self._end_trading_day = value

    @property
    def bar_count(self):
        """

        :return:
        """
        return self._bar_count

    @bar_count.setter
    def bar_count(self, value):
        self._bar_count = value

    @property
    def period(self):
        """

        :return:
        """
        return self._period

    @period.setter
    def period(self, value):
        self._period = value

    @property
    def trading_day_indices(self):
        """

        :return:
        """
        return self._trading_day_indices

    @trading_day_indices.setter
    def trading_day_indices(self, value):
        self._trading_day_indices = value

    @property
    def natural_day_indices(self):
        """

        :return:
        """
        return self._natural_day_indices

    @natural_day_indices.setter
    def natural_day_indices(self, value):
        self._natural_day_indices = value

    def mark_as_dirty(self, value):
        """

        :param value:
        """
        self._isDirty = value

    def read(self, reader):
        """
        读取头
        :param reader:
        """
        reader.stream.seek(0, 0)
        self._file_version = reader.read_string()
        reader.stream.seek(self.FileVersionSize, 0)
        self._market = EnumMarket(reader.read_int32())
        self._bar_type = EnumBarType(reader.read_int32())
        self._period = reader.read_int32()
        self._begin_time = CSharpUtils.convert_c_sharp_ticks_to_py_date_time(reader.read_int64())
        self._end_time = CSharpUtils.convert_c_sharp_ticks_to_py_date_time(reader.read_int64())
        self._begin_trading_day = CSharpUtils.convert_c_sharp_ticks_to_py_date_time(reader.read_int64())
        self._end_trading_day = CSharpUtils.convert_c_sharp_ticks_to_py_date_time(reader.read_int64())
        self._bar_count = reader.read_int32()
        reader.stream.seek(self.FileHeaderSize, 0)
        self._trading_day_indices.read(reader)
        self._natural_day_indices.read(reader)
        self.mark_as_dirty(False)

    def write(self, writer):
        if self._isDirty:
            writer.stream.seek(0, 0)
            writer.write_var_string(self.file_version)
            writer.stream.seek(self.FileVersionSize, 0)
            writer.write_int32(self.market.value)
            writer.write_int32(self.bar_type.value)
            writer.write_int32(self.period)
            writer.write_int64(CSharpUtils.get_c_sharp_ticks(self.begin_time))
            writer.write_int64(CSharpUtils.get_c_sharp_ticks(self.end_time))
            writer.write_int64(CSharpUtils.get_c_sharp_ticks(self.begin_trading_day))
            writer.write_int64(CSharpUtils.get_c_sharp_ticks(self.end_trading_day))
            writer.write_int32(self.bar_count)
            writer.stream.seek(self.FileHeaderSize, 0)
            self._trading_day_indices.write(writer)
            self._natural_day_indices.write(writer)
            self.mark_as_dirty(False)
