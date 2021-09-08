import datetime
import os
import sys
from decimal import Decimal

from SapphireQuant.Core.Bar import Bar
from SapphireQuant.DataProcessing.BinaryReader import BinaryReader
from SapphireQuant.DataProcessing.BinaryWriter import BinaryWriter


class BinaryDayBarStream(object):
    """
    日线读取流
    """
    CFileHeaderLen = 64
    CBarLen = 12 * 4
    CReserve = 48  # 空的预留字段
    CPosEnd = 8

    def __init__(self, market, instrument_id, file_path):
        self._tick_count = 0
        self._valid = False
        self._first_read = False
        self._begin_date = datetime.datetime.max
        self._end_date = datetime.datetime.max

        self._instrument_id = instrument_id.split('.')[0]
        self._file_path = file_path
        self._first_read = True

    def _read_header(self, reader):
        """
        读取头文件
        :param reader:
        """
        reader.stream.seek(0, 0)
        interval = reader.read_int16()
        bar_type = reader.read_int16()
        if (bar_type != 4) or (interval != 1):
            print("Wrong Day Kline Flag!!!")

        year = reader.read_int16()
        month = reader.read_byte()
        day = reader.read_byte()
        self._begin_date = datetime.datetime(year, month, day)

        year = reader.read_int16()
        month = reader.read_byte()
        day = reader.read_byte()
        self._end_date = datetime.datetime(year, month, day)

        if (self._begin_date == datetime.datetime.max) or (self._end_date == datetime.datetime.max) or (self._begin_date > self._end_date):
            raise Exception("Invalid Kline Date")

        self._tick_count = reader.read_int32()
        length = os.path.getsize(self._file_path)
        if self._tick_count != int(((length - self.CFileHeaderLen) / self.CBarLen)):
            raise Exception("Day KLine File Broken!!!")
        self._first_read = False

    def _read_bars(self, reader, bar_series, begin_date, end_date):
        """
        读取bars
        :param reader:
        :param bar_series:
        :param begin_date:
        :param end_date:
        """
        reader.stream.seek(self.CFileHeaderLen, 0)
        begin_date = datetime.datetime(begin_date.year, begin_date.month, begin_date.day)
        end_date = datetime.datetime(end_date.year, end_date.month, end_date.day)
        i = 0
        for i in range(0, self._tick_count):
            year = reader.read_int16()
            month = reader.read_byte()
            day = reader.read_byte()
            reader.stream.seek(self.CBarLen - 4, 1)
            trading_date = datetime.datetime(year, month, day)
            if trading_date >= begin_date:
                reader.stream.seek(-self.CBarLen, 1)
                break

        for index in range(i, self._tick_count):
            year = reader.read_int16()
            month = reader.read_byte()
            day = reader.read_byte()

            trading_date = datetime.datetime(year, month, day)

            if trading_date > end_date:
                break

            bar = Bar()
            bar.begin_time = trading_date
            bar.end_time = trading_date
            bar.open = reader.read_int32() / 1000.0
            bar.close = reader.read_int32() / 1000.0
            bar.high = reader.read_int32() / 1000.0
            bar.low = reader.read_int32() / 1000.0
            bar.pre_close = reader.read_int32() / 1000.0
            bar.volume = reader.read_double()
            bar.turnover = reader.read_double()
            bar.open_interest = reader.read_double()
            # bar.IsCompleted = True
            bar.trading_date = trading_date
            bar.instrument_id = self._instrument_id

            bar_series.append(bar)

    def read(self, bar_series, begin_date, end_date):
        """
        读取日线
        :param bar_series:
        :param begin_date:
        :param end_date:
        :return:
        """
        try:
            if not os.path.exists(self._file_path):
                self._first_read = True
                self._valid = False
                print("Read Day Kline Failed,Do Not Exist File:{0}".format(self._file_path))
                return False

            stream = open(self._file_path, 'rb+')
            length = os.path.getsize(self._file_path)
            if (length - self.CFileHeaderLen) % self.CBarLen != 0:
                raise Exception("Day Kline File Is Broken,Data Wrong!!!")

            reader = BinaryReader(stream)

            if self._first_read:
                self._read_header(reader)

            self._read_bars(reader, bar_series, begin_date, end_date)
            self._valid = True
            return True
        except Exception as e:
            self._first_read = True
            self._valid = False
            print("Read Day Kline Failed:{0},{1}".format(self._file_path, str(e)))
        finally:
            pass

        return False

    def read_all(self, bar_series):
        """

        :param bar_series:
        :return:
        """
        try:
            if not os.path.exists(self._file_path):
                self._first_read = True
                self._valid = False
                print("Read Day Kline Failed,Do Not Exist File:{0}".format(self._file_path))
                return False

            stream = open(self._file_path, 'rb+')
            length = os.path.getsize(self._file_path)
            if (length - self.CFileHeaderLen) % self.CBarLen != 0:
                raise Exception("Day Kline File Is Broken,Data Wrong!!!")

            reader = BinaryReader(stream)
            if self._first_read:
                self._read_header(reader)

            self._read_bars(reader, bar_series, self._begin_date, self._end_date)
            self._valid = True
            return True
        except Exception as e:
            self._first_read = True
            self._valid = False
            print("Read Day Kline Failed:{0},{1}".format(self._file_path, str(e)))
        finally:
            pass

        return False

    def _write_header(self, writer):
        writer.stream.seek(0, 0)
        writer.write_int16(1)
        writer.write_int16(4)
        writer.write_int16(self._begin_date.year)
        writer.write_byte(self._begin_date.month)
        writer.write_byte(self._begin_date.day)
        writer.write_int16(self._end_date.year)
        writer.write_byte(self._end_date.month)
        writer.write_byte(self._end_date.day)
        writer.write_int32(self._tick_count)

        buffer = bytearray(self.CReserve)
        writer.write_bytes(buffer)

    def _write_bars(self, bar_series, writer, start, count):
        end = start+count
        for i in range(start, end, 1):
            bar = bar_series[i]

            writer.write_int16(bar.begin_time.year)
            writer.write_byte(bar.begin_time.month)
            writer.write_byte(bar.begin_time.day)

            self.write_float_with_decimal(writer, bar.open)
            self.write_float_with_decimal(writer, bar.close)
            self.write_float_with_decimal(writer, bar.high)
            self.write_float_with_decimal(writer, bar.low)
            self.write_float_with_decimal(writer, bar.pre_close)
            writer.write_double(bar.volume)
            writer.write_double(bar.turnover)
            writer.write_double(bar.open_interest)

    @staticmethod
    def write_float_with_decimal(writer, value):
        """

        :param writer:
        :param value:
        """
        if value < sys.float_info.max:
            value = Decimal.from_float(value)
            writer.write_int32(int(round(value * Decimal.from_float(1000), 0)))
        else:
            writer.write_int32(0)

    def write(self, bar_series):
        """

        :param bar_series:
        """
        if bar_series is None or len(bar_series) == 0:
            return True

        try:
            with open(self._file_path, 'wb') as stream:
                self._tick_count = len(bar_series)
                self._begin_date = bar_series[0].trading_date
                self._end_date = bar_series[-1].trading_date

                writer = BinaryWriter(stream)
                self._write_header(writer)
                self._write_bars(bar_series, writer, 0, self._tick_count)

            return True
        except Exception as e:
            print('Write Day Bar Error:{0}'.format(str(e)))
        return False

    def append(self, bar_series):
        """
        Append Bar Series
        :param bar_series:
        """
        if not os.path.exists(self._file_path) or sys.getsizeof(self._file_path) < self.CFileHeaderLen:
            return self.write(bar_series)

        try:
            with open(self._file_path, 'rb+') as stream:
                reader = BinaryReader(stream)
                self._read_header(reader)
                count = len(bar_series)

                self._tick_count = int((sys.getsizeof(self._file_path) - self.CFileHeaderLen)/self.CBarLen)
                self._tick_count += count
                self._end_date = bar_series[-1].trading_date

                writer = BinaryWriter(stream)
                self._write_header(writer)
                writer.stream.seek(0, 2)
                self._write_bars(bar_series, writer, 0, count)

            return True
        except Exception as e:
            print('Append Day Bar Error:{0}'.format(str(e)))
        return False
