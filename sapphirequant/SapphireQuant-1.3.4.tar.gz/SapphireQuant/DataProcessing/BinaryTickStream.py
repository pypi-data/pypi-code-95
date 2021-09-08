import datetime
import os
import sys
from decimal import Decimal

from SapphireQuant.Config.TradingDay.TradingDayHelper import TradingDayHelper
from SapphireQuant.Core.CSharpUtils import CSharpUtils
from SapphireQuant.Core.Quote import Quote
from SapphireQuant.Core.Tick import Tick
from SapphireQuant.DataProcessing.BinaryReader import BinaryReader
from SapphireQuant.DataProcessing.BinaryWriter import BinaryWriter


class BinaryTickStream:
    """
    Tick读写流
    """
    CFileFlag = 1262700884  # ('K' << 24) + ('C' << 16) + ('I' << 8) + 'T'
    CFileHeaderLen = 44
    CNaturalDayLen = 8 * 4  # 正常可以放置4个自然日索引
    CTickOffset = CFileHeaderLen + CNaturalDayLen  # 76  Tick数据开始的位置

    # VersionNew
    CTickHeaderLenV0 = 32  # 不带LocalTime
    CTickHeaderLenV1 = 40  # 带LocalTime
    CTickQuoteLen = 4 * 4  # 买一价，卖一价，买一量，卖一量

    # VersionOld
    CFileHeaderLenOld = 64
    CReserveOld = 27
    CTickHeaderLenOld = 32

    def __init__(self, market, instrument_id, exchange_id, file_path):
        self._file_path = ""
        self._instrument_id = ""
        self._exchange_id = ""
        self._market = 0
        self._first_read = False
        self._new_version = True

        # Header
        self._version = 1
        self._quote_level = 1
        self._multi_unit = 1000
        self._trading_day = datetime.datetime.max
        self._pre_close_price = 0.0
        self._pre_settlement_price = 0.0
        self._pre_interest = 0.0
        self._up_limit = 0.0
        self._down_limit = 0.0
        self._open_price = 0.0
        self._tick_count = 0
        self._natural_day_count = 1
        self._natural_day_offset = 0
        self._tick_offset = 0

        # NaturalDay
        self._natural_days = []
        self._natural_day_tick_offset = []

        # 18点后
        self._pre_trading_day1 = datetime.datetime.max
        # 9点前
        self._pre_trading_day2 = datetime.datetime.max

        self._file_path = file_path
        self._instrument_id = instrument_id
        self._exchange_id = exchange_id
        self._first_read = True
        self._market = market

    def _read_header(self, reader):
        """
        读取头
        :param reader:
        :return:
        """
        reader.stream.seek(0, 0)
        flag = reader.read_int32()
        if flag != self.CFileFlag:
            return False
        self._natural_days.clear()
        self._natural_day_tick_offset.clear()
        self._natural_day_count = 0

        self._version = reader.read_int16()
        self._quote_level = reader.read_byte()

        tmp = 1
        multi = reader.read_byte()
        for i in range(0, multi):
            tmp = tmp * 10

        self._multi_unit = tmp

        year = reader.read_int16()
        month = reader.read_byte()
        day = reader.read_byte()

        self._trading_day = datetime.datetime(year, month, day)

        self._pre_close_price = reader.read_int32() / self._multi_unit
        self._pre_settlement_price = reader.read_int32() / self._multi_unit
        self._pre_interest = reader.read_int32()
        self._up_limit = reader.read_int32() / self._multi_unit
        self._down_limit = reader.read_int32() / self._multi_unit
        self._open_price = reader.read_int32() / self._multi_unit
        self._tick_count = reader.read_int32()

        orig = reader.read_int16()
        self._natural_day_count = (orig >> 12)
        self._natural_day_offset = (orig & 0x0fff)
        self._tick_offset = reader.read_int16()
        return True

    def _read_old_header(self, reader):
        """
        读取老版的头
        :param reader:
        """
        reader.stream.seek(0, 0)
        self._natural_days.clear()
        self._natural_day_tick_offset.clear()
        self._natural_day_count = 0

        interval = reader.read_int16()
        bar_type = reader.read_int16()
        if (bar_type & 0xff) != 0:
            raise Exception("错误的tick数据文件标识")

        self._new_version = False
        if ((bar_type >> 10) & 0x3) == 1:
            self._multi_unit = 1000
        else:
            self._multi_unit = 100

        year = reader.read_int16()
        month = reader.read_byte()
        day = reader.read_byte()

        self._trading_day = datetime.datetime(year, month, day)
        self._pre_trading_day1 = TradingDayHelper.get_pre_trading_day(self._trading_day)
        self._pre_trading_day2 = self._pre_trading_day1 + datetime.timedelta(days=1)

        self._pre_close_price = reader.read_int32() / self._multi_unit
        self._pre_settlement_price = reader.read_int32() / self._multi_unit
        self._pre_interest = reader.read_int32()
        self._up_limit = reader.read_int32() / self._multi_unit
        self._down_limit = reader.read_int32() / self._multi_unit
        self._open_price = reader.read_int32() / self._multi_unit
        self._tick_count = reader.read_int32()
        self._quote_level = reader.read_byte()

        reader.read_bytes(self.CReserveOld)

    def _read_natural_days(self, reader):
        """
        读取自然日索引
        :param reader:
        """
        reader.stream.seek(self._natural_day_offset, 0)
        for i in range(0, self._natural_day_count):
            year = reader.read_int16()
            month = reader.read_byte()
            day = reader.read_byte()
            natural_day_tick_offset = reader.read_int32()

            natural_day = datetime.datetime(year, month, day)

            self._natural_days.append(natural_day)
            self._natural_day_tick_offset.append(natural_day_tick_offset)

    def _read_tick(self, reader, natural_day):
        """
        读取Tick
        :param reader:
        :param natural_day:
        """
        tick = Tick()
        tick.market = self._market
        tick.open_price = self._open_price
        tick.pre_close_price = self._pre_close_price
        tick.instrument_id = self._instrument_id
        tick.exchange_id = self._exchange_id
        tick.pre_open_interest = self._pre_interest
        tick.pre_settlement_price = self._pre_settlement_price
        tick.up_limit = self._up_limit
        tick.drop_limit = self._down_limit

        hour = reader.read_byte()
        minute = reader.read_byte()
        second = reader.read_byte()
        milliseconds = reader.read_byte()
        milliseconds *= 10

        tick.date_time = datetime.datetime(natural_day.year, natural_day.month, natural_day.day, hour, minute, second, milliseconds * 1000)

        if self._version == 1:
            c_sharp_ticks = reader.read_int64()
            tick.local_time = CSharpUtils.convert_c_sharp_ticks_to_py_date_time(c_sharp_ticks)
        else:
            tick.local_time = datetime.datetime.today()
        tick.trading_date = self._trading_day
        tick.last_price = reader.read_int32() / self._multi_unit
        tick.high_price = reader.read_int32() / self._multi_unit
        tick.low_price = reader.read_int32() / self._multi_unit
        tick.open_interest = reader.read_int32() / self._multi_unit
        tick.volume = reader.read_int32()
        tick.turnover = reader.read_double()
        quote = Quote()
        quote.ask_volume1 = reader.read_int32()
        quote.bid_volume1 = reader.read_int32()
        quote.ask_price1 = reader.read_int32() / self._multi_unit
        quote.bid_price1 = reader.read_int32() / self._multi_unit
        tick.quote = quote
        return tick

    def _read_tick_old(self, reader):
        """
        读取Tick
        :param reader:
        """
        tick = Tick()
        tick.market = self._market
        tick.open_price = self._open_price
        tick.pre_close_price = self._pre_close_price
        tick.instrument_id = self._instrument_id
        tick.exchange_id = self._exchange_id
        tick.pre_open_interest = self._pre_interest
        tick.pre_settlement_price = self._pre_settlement_price
        tick.up_limit = self._up_limit
        tick.drop_limit = self._down_limit

        hour = reader.read_byte()
        minute = reader.read_byte()
        second = reader.read_byte()
        milliseconds = reader.read_byte()
        milliseconds *= 10

        tick.trading_date = self._trading_day
        if hour < 7:
            tick.date_time = datetime.datetime(self._pre_trading_day2.year, self._pre_trading_day2.month,
                                               self._pre_trading_day2.day, hour, minute, second, milliseconds)
        elif hour < 18:
            tick.date_time = datetime.datetime(self._trading_day.year, self._trading_day.month,
                                               self._trading_day.day, hour, minute, second, milliseconds)
        else:
            tick.date_time = datetime.datetime(self._pre_trading_day1.year, self._pre_trading_day1.month,
                                               self._pre_trading_day1.day, hour, minute, second, milliseconds)

        tick.last_price = reader.read_int32() / self._multi_unit
        tick.high_price = reader.read_int32() / self._multi_unit
        tick.low_price = reader.read_int32() / self._multi_unit
        tick.open_interest = reader.read_int32() / self._multi_unit
        tick.volume = reader.read_int32()
        tick.turnover = reader.read_double()
        quote = Quote()
        quote.ask_volume1 = reader.read_int32()
        quote.bid_volume1 = reader.read_int32()
        quote.ask_price1 = reader.read_int32() / self._multi_unit
        quote.bid_price1 = reader.read_int32() / self._multi_unit
        tick.quote = quote
        return tick

    def _read_ticks_by_count(self, tick_series, reader, offset, count):
        """
        读取V1版本的Level1行情
        :param tick_series:
        :param reader:
        :param offset:
        :param count:
        :return:
        """
        pos = self._tick_offset + offset * (self.CTickHeaderLenV1 + self._quote_level * self.CTickQuoteLen)
        reader.stream.seek(pos)
        natural_index = 0
        for natural_index in range(0, len(self._natural_day_tick_offset)):
            if offset < self._natural_day_tick_offset[natural_index]:
                break
            natural_index = natural_index + 1

        natural_index = natural_index - 1
        if natural_index < 0:
            return

        natural_day = self._natural_days[natural_index]
        next_natural_day_tick_offset = 100000000
        if natural_index < len(self._natural_day_tick_offset) - 1:
            next_natural_day_tick_offset = self._natural_day_tick_offset[natural_index + 1] - 1

        read_tick_count = self._tick_count - offset
        if read_tick_count < count:
            read_tick_count = read_tick_count
        else:
            read_tick_count = count

        for i in range(0, read_tick_count):
            tick = self._read_tick(reader, natural_day)
            tick_series.append(tick)

            if i + offset >= next_natural_day_tick_offset:
                natural_index = natural_index + 1
                if natural_index < len(self._natural_days):
                    natural_day = self._natural_days[natural_index]

                next_natural_day_tick_offset = 10000000
                if natural_index < len(self._natural_day_tick_offset) - 1:
                    next_natural_day_tick_offset = self._natural_day_tick_offset[natural_index + 1] - 1

    def _read_ticks_by_count_old(self, tick_series, reader, offset, count):
        """

        :param tick_series:
        :param reader:
        :param offset:
        :param count:
        """
        pos = self.CFileHeaderLenOld + offset * (self.CTickHeaderLenOld + self._quote_level * self.CTickQuoteLen)
        reader.stream.seek(pos)
        read_tick_count = self._tick_count - offset
        if read_tick_count < count:
            read_tick_count = read_tick_count
        else:
            read_tick_count = count

        for i in range(0, read_tick_count):
            tick = self._read_tick_old(reader)
            tick_series.append(tick)

    def _read_ticks_by_time(self, tick_series, reader, begin_time, end_time):
        """

        :param tick_series:
        :param reader:
        :param begin_time:
        :param end_time:
        :return:
        """
        reader.stream.seek(self._tick_offset, 0)
        if len(self._natural_days) == 0:
            return

        natural_index = 0
        natural_day = self._natural_days[natural_index]
        next_natural_day_tick_offset = sys.maxsize
        if natural_index < len(self._natural_day_tick_offset) - 1:
            next_natural_day_tick_offset = self._natural_day_tick_offset[natural_index + 1] - 1

        blk_len = self.CTickHeaderLenV1 + self._quote_level * self.CTickQuoteLen - 4

        for i in range(self._tick_count):
            hour = reader.read_byte()
            minute = reader.read_byte()
            second = reader.read_byte()
            milliseconds = reader.read_byte()
            milliseconds *= 10

            date_time = datetime.datetime(natural_day.year, natural_day.month, natural_day.day, hour, minute, second, milliseconds)

            if date_time > end_time:
                return

            if date_time < begin_time:
                if i >= next_natural_day_tick_offset:
                    natural_index += 1

                    if natural_index < len(self._natural_days):
                        natural_day = self._natural_days[natural_index]

                    next_natural_day_tick_offset = sys.maxsize
                    if natural_index < (len(self._natural_day_tick_offset) - 1):
                        next_natural_day_tick_offset = self._natural_day_tick_offset[natural_index + 1] - 1
                reader.read_bytes(blk_len)
                continue

            tick = self._read_tick(reader, natural_day)
            tick_series.append(tick)

            if i >= next_natural_day_tick_offset:
                natural_index += 1
                if natural_index < len(self._natural_days):
                    natural_day = self._natural_days[natural_index]

                next_natural_day_tick_offset = sys.maxsize
                if natural_index < len(self._natural_day_tick_offset) - 1:
                    next_natural_day_tick_offset = self._natural_day_tick_offset[natural_index + 1] - 1

    def _read_ticks_by_time_old(self, tick_series, reader, begin_time, end_time):
        """

        :param tick_series:
        :param reader:
        :param begin_time:
        :param end_time:
        :return:
        """
        reader.stream.seek(self.CFileHeaderLenOld, 0)
        blk_len = self.CTickHeaderLenV0 + self._quote_level * self.CTickQuoteLen - 4

        for i in range(self._tick_count):
            hour = reader.read_byte()
            minute = reader.read_byte()
            second = reader.read_byte()
            millisecond = reader.read_byte()
            millisecond *= 10

            if hour < 7:
                tick_time = datetime.datetime(self._pre_trading_day2.year, self._pre_trading_day2.month,
                                              self._pre_trading_day2.day, hour, minute, second, millisecond)
            elif hour < 18:
                tick_time = datetime.datetime(self._trading_day.year, self._trading_day.month,
                                              self._trading_day.day, hour, minute, second, millisecond)
            else:
                tick_time = datetime.datetime(self._pre_trading_day1.year, self._pre_trading_day1.month,
                                              self._pre_trading_day1.day, hour, minute, second, millisecond)

            if tick_time > end_time:
                return

            if tick_time < begin_time:
                reader.read_bytes(blk_len)
                continue

            tick = self._read_tick_old(reader)
            tick_series.append(tick)

    def read_last_tick(self):
        """
        根据个数读取
        :return:
        """
        if not os.path.exists(self._file_path):
            _firstRead = True
            print("Read Future Tick Data Failed:{},File Do Not Exist....".format(self._file_path))
            return None

        stream = open(self._file_path, 'rb')
        reader = BinaryReader(stream)

        if self._first_read:
            if self._read_header(reader):
                self._read_natural_days(reader)
            else:
                self._read_old_header(reader)
            _firstRead = False

        tick_series = []
        offset = self._tick_count - 1
        count = 1
        if self._new_version:
            if self._quote_level == 1:
                self._read_ticks_by_count(tick_series, reader, offset, count)
            else:
                raise Exception("不支持" + str(self._quote_level) + "档盘口")
        else:
            if self._quote_level == 1:
                self._read_ticks_by_count_old(tick_series, reader, offset, count)
            else:
                raise Exception("不支持" + str(self._quote_level) + "档盘口")
        stream.close()
        if len(tick_series) > 0:
            return tick_series[0]
        return None

    def read_by_count(self, tick_series, offset, count):
        """
        根据个数读取
        :param tick_series:
        :param offset:跳多少个Tick去取数据
        :param count:
        :return:
        """
        if not os.path.exists(self._file_path):
            _firstRead = True
            print("Read Tick Data Error,Do Not Exist File:{0}".format(self._file_path))
            return False

        stream = open(self._file_path, 'rb')
        reader = BinaryReader(stream)

        if self._first_read:
            if self._read_header(reader):
                self._read_natural_days(reader)
            else:
                self._read_old_header(reader)
            _firstRead = False

        if self._new_version:
            if self._quote_level == 1:
                self._read_ticks_by_count(tick_series, reader, offset, count)
            else:
                raise Exception("Do Not Support {0} Quote Level......".format(str(self._quote_level)))
        else:
            if self._quote_level == 1:
                self._read_ticks_by_count_old(tick_series, reader, offset, count)
            else:
                raise Exception("不支持" + str(self._quote_level) + "档盘口")
        stream.close()
        return True

    def read_by_time(self, tick_series, begin_time, end_time):
        """
        根据时间读取Tick
        :param tick_series:
        :param begin_time:
        :param end_time:
        :return:
        """
        if (begin_time is None) and (end_time is None):
            return self.read_by_count(0, 0, sys.maxsize)

        if end_time is None:
            end_time = datetime.datetime.max

        try:
            if not os.path.exists(self._file_path):
                _firstRead = True
                print("Read Tick Data Error,Do Not Exist File:{0}".format(self._file_path))
                return False

            stream = open(self._file_path, 'rb')
            reader = BinaryReader(stream)

            if self._first_read:
                if self._read_header(reader):
                    self._read_natural_days(reader)
                else:
                    self._read_old_header(reader)
                _firstRead = False

            if self._new_version:
                if self._quote_level == 1:
                    self._read_ticks_by_time(tick_series, reader, begin_time, end_time)
                else:
                    raise Exception("不支持" + str(self._quote_level) + "档盘口")
            else:
                if self._quote_level == 1:
                    self._read_ticks_by_time_old(tick_series, reader, begin_time, end_time)
                else:
                    raise Exception("不支持" + str(self._quote_level) + "档盘口")
            stream.close()
            return True
        except Exception as e:
            print("Read Tick Data By Time Error:{0}".format(str(e)))

        return False

    def _write_header(self, writer):
        """
        写头
        :param writer:
        """
        writer.stream.seek(0, 0)
        writer.write_int32(self.CFileFlag)
        writer.write_int16(self._version)
        writer.write_byte(self._quote_level)
        multi = 0
        tmp = self._multi_unit
        while tmp != 0:
            tmp = int(tmp / 10)
            multi += 1

        multi -= 1
        if multi < 0:
            raise Exception("write multi error")

        writer.write_byte(multi)
        writer.write_int16(self._trading_day.year)
        writer.write_byte(self._trading_day.month)
        writer.write_byte(self._trading_day.day)
        self._write_float_with_decimal(writer, self._pre_close_price)
        self._write_float_with_decimal(writer, self._pre_settlement_price)
        self._write_float_with_decimal(writer, self._pre_interest)
        self._write_float_with_decimal(writer, self._up_limit)
        self._write_float_with_decimal(writer, self._down_limit)
        self._write_float_with_decimal(writer, self._open_price)

        buffer = bytearray(self.CNaturalDayLen + 8)
        writer.write_bytes(buffer)

    def _write_natural_days(self, writer):
        """

        :param writer:
        """
        writer.stream.seek(self.CFileHeaderLen - 8, 0)
        writer.write_int32(self._tick_count)
        tmp = (len(self._natural_days) << 12) + self.CFileHeaderLen
        writer.write_int16(tmp)
        writer.write_int16(self.CTickOffset)
        for i in range(len(self._natural_days)):
            natural_day = self._natural_days[i]
            natural_day_tick_offset = self._natural_day_tick_offset[i]

            writer.write_int16(natural_day.year)
            writer.write_byte(natural_day.month)
            writer.write_byte(natural_day.day)
            writer.write_int32(natural_day_tick_offset)

    def _write_ticks(self, tick_list, writer, offset, count):
        """
        写入
        """
        natural_day = datetime.datetime.max
        if len(self._natural_days) > 0:
            natural_day = self._natural_days[-1]

        end = offset + count
        for i in range(offset, end, 1):
            if i >= end:
                break
            tick = tick_list[i]
            tick_date = datetime.datetime(tick.date_time.year, tick.date_time.month, tick.date_time.day)
            if tick_date != natural_day:
                if len(self._natural_days) > 0:
                    if tick_date < self._natural_days[-1]:
                        print('Tick Date Error,Tick Natural Date={0},File Date={1}'.format(tick_date.strftime('%Y%m%d'), self._natural_days[-1].strftime('%Y%m%d')))
                    if tick_date == self._natural_days[-1]:
                        natural_day = self._natural_days[-1]
                    else:
                        natural_day = tick_date
                        natural_tick_offset = self._tick_count
                        self._natural_days.append(natural_day)
                        self._natural_day_tick_offset.append(natural_tick_offset)
                else:
                    natural_day = tick_date
                    natural_tick_offset = self._tick_count
                    self._natural_days.append(natural_day)
                    self._natural_day_tick_offset.append(natural_tick_offset)

            writer.write_byte(tick.date_time.hour)
            writer.write_byte(tick.date_time.minute)
            writer.write_byte(tick.date_time.second)
            writer.write_byte(int(tick.date_time.microsecond / 1000 / 10))
            c_sharp_ticks = CSharpUtils.get_c_sharp_ticks(tick.local_time)
            writer.write_int64(c_sharp_ticks)

            self._write_float_with_decimal(writer, tick.last_price)
            self._write_float_with_decimal(writer, tick.high_price)
            self._write_float_with_decimal(writer, tick.low_price)
            self._write_float_with_decimal(writer, tick.open_interest)

            writer.write_int32(tick.volume)
            writer.write_double(tick.turnover)
            writer.write_int32(tick.quote.ask_volume1)
            writer.write_int32(tick.quote.bid_volume1)
            self._write_float_with_decimal(writer, tick.ask_price1)
            self._write_float_with_decimal(writer, tick.bid_price1)
            self._tick_count += 1

    def _write_float_with_decimal(self, writer, value):
        """

        :param writer:
        :param value:
        """
        if value < sys.float_info.max:
            value = Decimal.from_float(value)
            writer.write_int32(int(round(value * Decimal.from_float(self._multi_unit), 0)))
        else:
            writer.write_int32(0)

    def _update_tick_open_price(self, tick_list, writer):
        """
        更新开盘价
        :param tick_list:
        :param writer:
        """
        if len(tick_list) > 0:
            open_price = tick_list[0].open_price
            if abs(open_price - self._open_price) >= 0.000000001:
                writer.stream.seek(32, 0)
                self._write_float_with_decimal(writer, open_price)

    def write(self, tick_list, start, length, quote_level):
        """

        :param tick_list:
        :param start:
        :param length:
        :param quote_level:
        :return:
        """
        if len(tick_list) == 0:
            return True

        try:
            self._natural_day_count = 0
            self._natural_days.clear()
            self._natural_day_tick_offset.clear()

            self._multi_unit = 1000

            self._trading_day = tick_list[0].trading_date
            self._pre_close_price = tick_list[0].pre_close_price
            self._open_price = tick_list[0].open_price
            self._pre_interest = tick_list[0].pre_open_interest
            self._pre_settlement_price = tick_list[0].pre_settlement_price
            self._up_limit = tick_list[0].up_limit
            self._down_limit = tick_list[0].drop_limit
            self._quote_level = quote_level

            count = len(tick_list) - start
            if length < count:
                count = length

            self._tick_count = 0
            stream = open(self._file_path, 'wb')
            writer = BinaryWriter(stream)
            self._write_header(writer)

            if self._quote_level == 1:
                self._write_ticks(tick_list, writer, start, count)
            elif self._quote_level == 5:
                pass

            self._write_natural_days(writer)
            stream.flush()
            stream.close()

            return True
        except Exception as e:
            print('Write Ticks Error:{0}'.format(str(e)))

    def append(self, tick_list, start, length, quote_level):
        """
        追加Tick
        :param tick_list:
        :param start:
        :param length:
        :param quote_level:
        :return:
        """
        if not os.path.exists(self._file_path):
            print('Append Tick, File Not Exist, Cover:{0}'.format(self._file_path))
            record_deep_dir = os.path.dirname(self._file_path)
            if not os.path.exists(record_deep_dir):
                os.makedirs(record_deep_dir)
            return self.write(tick_list, start, length, quote_level)
        if os.path.getsize(self._file_path) < self.CFileHeaderLen + self.CNaturalDayLen:
            print('Append Tick, File Size Error, Cover:{0}'.format(self._file_path))
            return self.write(tick_list, start, length, quote_level)
        if (os.path.getsize(self._file_path) - self.CTickOffset) % (self.CTickHeaderLenV1 + quote_level * self.CTickQuoteLen) != 0:
            print('Append Tick, File Layout Error, Cover:{0}'.format(self._file_path))
            return self._write_ticks(tick_list, start, length, quote_level)
        try:
            stream = open(self._file_path, 'rb+')
            reader = BinaryReader(stream)
            if self._first_read:
                self._read_header(reader)
                self._read_natural_days(reader)
                self._first_read = True

            if self._quote_level != quote_level:
                raise Exception("Append Tick Error,Quote Level:File={0},Tick={1}".format(self._quote_level, quote_level))

            tick_count = int((os.path.getsize(self._file_path) - self.CTickOffset) / (self.CTickHeaderLenV1 + quote_level * self.CTickQuoteLen))
            if tick_count != self._tick_count:
                print("File Tick Count:{0} Not Equals Cache Tick Count:{1},File Path:{2}".format(tick_count, self._tick_count, self._file_path))

            self._tick_count = tick_count

            count = len(tick_list) - start
            if length < count:
                count = length

            writer = BinaryWriter(stream)
            self._update_tick_open_price(tick_list, writer)
            stream.seek(0, 2)
            if self._quote_level == 1:
                self._write_ticks(tick_list, writer, start, count)
            else:
                pass

            self._write_natural_days(writer)
            stream.flush()
            stream.close()
            return True

        except Exception as e:
            self._first_read = False
            print("Append Tick Error:{0},{1}".format(self._file_path, str(e)))
        return False
