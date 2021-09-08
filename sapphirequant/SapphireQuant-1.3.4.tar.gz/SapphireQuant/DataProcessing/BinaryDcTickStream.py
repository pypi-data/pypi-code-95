import datetime
import os
import sys
from SapphireQuant.Core.CSharpUtils import CSharpUtils
from SapphireQuant.Core.Quote import Quote
from SapphireQuant.Core.Tick import Tick
from SapphireQuant.DataProcessing.BinaryReader import BinaryReader
from SapphireQuant.DataProcessing.BinaryWriter import BinaryWriter


class BinaryDcTickStream:
    """
    Tick读写流
    """
    CFileFlag = 1262700884  # ('K' << 24) + ('C' << 16) + ('I' << 8) + 'T'
    CFileHeaderLen = 58

    CTickHeaderLenV1 = 64  # 带LocalTime
    CTickQuoteLen = 5 * 32  # 买一价，卖一价，买一量，卖一量

    def __init__(self, market, instrument_id, exchange_id, file_path):
        self._file_path = file_path
        self._instrument_id = instrument_id
        self._exchange_id = exchange_id
        self._market = market

        # Header
        self._version = 1
        self._trading_day = datetime.datetime.max
        self._pre_close_price = 0.0
        self._pre_settlement_price = 0.0
        self._pre_interest = 0.0
        self._up_limit = 0.0
        self._down_limit = 0.0
        self._open_price = 0.0

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
        self._version = reader.read_int16()

        year = reader.read_int16()
        month = reader.read_byte()
        day = reader.read_byte()

        self._trading_day = datetime.datetime(year, month, day)

        self._pre_close_price = reader.read_double()
        self._pre_settlement_price = reader.read_double()
        self._pre_interest = reader.read_double()
        self._up_limit = reader.read_double()
        self._down_limit = reader.read_double()
        self._open_price = reader.read_double()
        return True

    def _read_tick(self, reader):
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

        tick.date_time = CSharpUtils.convert_c_sharp_ticks_to_py_date_time(reader.read_int64())
        tick.local_time = CSharpUtils.convert_c_sharp_ticks_to_py_date_time(reader.read_int64())
        tick.trading_date = self._trading_day
        tick.last_price = reader.read_double()
        tick.high_price = reader.read_double()
        tick.low_price = reader.read_double()
        tick.open_interest = reader.read_double()
        tick.volume = reader.read_double()
        tick.turnover = reader.read_double()
        quote = Quote()
        quote.ask_volume1 = reader.read_double()
        quote.bid_volume1 = reader.read_double()
        quote.ask_price1 = reader.read_double()
        quote.bid_price1 = reader.read_double()

        quote.ask_volume2 = reader.read_double()
        quote.bid_volume2 = reader.read_double()
        quote.ask_price2 = reader.read_double()
        quote.bid_price2 = reader.read_double()

        quote.ask_volume3 = reader.read_double()
        quote.bid_volume3 = reader.read_double()
        quote.ask_price3 = reader.read_double()
        quote.bid_price3 = reader.read_double()

        quote.ask_volume4 = reader.read_double()
        quote.bid_volume4 = reader.read_double()
        quote.ask_price4 = reader.read_double()
        quote.bid_price4 = reader.read_double()

        quote.ask_volume5 = reader.read_double()
        quote.bid_volume5 = reader.read_double()
        quote.ask_price5 = reader.read_double()
        quote.bid_price5 = reader.read_double()
        tick.quote = quote
        return tick

    def _get_tick_count(self):
        tick_count = int((os.path.getsize(self._file_path) - self.CFileHeaderLen) / (self.CTickHeaderLenV1 + self.CTickQuoteLen))
        return tick_count

    def _read_ticks_by_count(self, tick_series, reader, offset, count):
        """
        读取V1版本的Level1行情
        :param tick_series:
        :param reader:
        :param offset:
        :param count:
        :return:
        """
        pos = self.CFileHeaderLen + offset * (self.CTickHeaderLenV1 + self.CTickQuoteLen)
        reader.stream.seek(pos)
        tick_count = self._get_tick_count()
        read_tick_count = tick_count - offset
        if read_tick_count < count:
            read_tick_count = read_tick_count
        else:
            read_tick_count = count

        for i in range(0, read_tick_count):
            tick = self._read_tick(reader)
            tick_series.append(tick)

    def _read_ticks_by_time(self, tick_series, reader, begin_time, end_time):
        """

        :param tick_series:
        :param reader:
        :param begin_time:
        :param end_time:
        :return:
        """
        reader.stream.seek(self.CFileHeaderLen, 0)
        tick_count = self._get_tick_count()
        blk_len = self.CTickHeaderLenV1 + self.CTickQuoteLen - 8
        for i in range(tick_count):
            date_time = CSharpUtils.convert_c_sharp_ticks_to_py_date_time(reader.read_int64())

            if date_time > end_time:
                return

            if date_time < begin_time:
                reader.read_bytes(blk_len)
                continue

            tick = self._read_tick(reader)
            tick_series.append(tick)

    def read_last_tick(self):
        """
        根据个数读取
        :return:
        """
        if not os.path.exists(self._file_path):
            _firstRead = True
            print(f"Read Future Tick Data Failed:{self._file_path},File Do Not Exist....")
            return None

        with open(self._file_path, 'rb') as stream:
            reader = BinaryReader(stream)
            self._read_header(reader)
            tick_count = self._get_tick_count()
            tick_series = []
            offset = tick_count - 1
            count = 1
            self._read_ticks_by_count(tick_series, reader, offset, count)

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
            print("Read Tick Data Error,Do Not Exist File:{0}".format(self._file_path))
            return False

        with open(self._file_path, 'rb') as stream:
            reader = BinaryReader(stream)
            self._read_header(reader)
            self._read_ticks_by_count(tick_series, reader, offset, count)
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
            return self.read_by_count(tick_series, 0, sys.maxsize)

        if end_time is None:
            end_time = datetime.datetime.max

        try:
            if not os.path.exists(self._file_path):
                print(f"Read Tick Data Error,Do Not Exist File:{self._file_path}")
                return False

            with open(self._file_path, 'rb') as stream:
                reader = BinaryReader(stream)
                self._read_header(reader)
                self._read_ticks_by_time(tick_series, reader, begin_time, end_time)
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
        writer.write_int16(self._trading_day.year)
        writer.write_byte(self._trading_day.month)
        writer.write_byte(self._trading_day.day)
        writer.write_double(self._pre_close_price)
        writer.write_double(self._pre_settlement_price)
        writer.write_double(self._pre_interest)
        writer.write_double(self._up_limit)
        writer.write_double(self._down_limit)
        writer.write_double(self._open_price)

    def _write_ticks(self, tick_list, writer, offset, count):
        """
        写入
        """
        end = offset + count
        for i in range(offset, end, 1):
            if i >= end:
                break
            tick = tick_list[i]
            writer.write_int64(CSharpUtils.get_c_sharp_ticks(tick.date_time))
            writer.write_int64(CSharpUtils.get_c_sharp_ticks(tick.local_time))

            writer.write_double(tick.last_price)
            writer.write_double(tick.high_price)
            writer.write_double(tick.low_price)
            writer.write_double(tick.open_interest)

            writer.write_double(tick.volume)
            writer.write_double(tick.turnover)

            writer.write_double(tick.quote.ask_volume1)
            writer.write_double(tick.quote.bid_volume1)
            writer.write_double(tick.quote.ask_price1)
            writer.write_double(tick.quote.bid_price1)

            writer.write_double(tick.quote.ask_volume2)
            writer.write_double(tick.quote.bid_volume2)
            writer.write_double(tick.quote.ask_price2)
            writer.write_double(tick.quote.bid_price2)

            writer.write_double(tick.quote.ask_volume3)
            writer.write_double(tick.quote.bid_volume3)
            writer.write_double(tick.quote.ask_price3)
            writer.write_double(tick.quote.bid_price3)

            writer.write_double(tick.quote.ask_volume4)
            writer.write_double(tick.quote.bid_volume4)
            writer.write_double(tick.quote.ask_price4)
            writer.write_double(tick.quote.bid_price4)

            writer.write_double(tick.quote.ask_volume5)
            writer.write_double(tick.quote.bid_volume5)
            writer.write_double(tick.quote.ask_price5)
            writer.write_double(tick.quote.bid_price5)

    def write(self, tick_list, start, length):
        """

        :param tick_list:
        :param start:
        :param length:
        :return:
        """
        if len(tick_list) == 0:
            return True

        try:
            self._trading_day = tick_list[0].trading_date
            self._pre_close_price = tick_list[0].pre_close_price
            self._open_price = tick_list[0].open_price
            self._pre_interest = tick_list[0].pre_open_interest
            self._pre_settlement_price = tick_list[0].pre_settlement_price
            self._up_limit = tick_list[0].up_limit
            self._down_limit = tick_list[0].drop_limit

            count = len(tick_list) - start
            if length < count:
                count = length

            with open(self._file_path, 'wb') as stream:
                writer = BinaryWriter(stream)
                self._write_header(writer)
                self._write_ticks(tick_list, writer, start, count)
                stream.flush()

            return True
        except Exception as e:
            print('Write Ticks Error:{0}'.format(str(e)))

    def append(self, tick_list, start, length):
        """
        追加Tick
        :param tick_list:
        :param start:
        :param length:
        :return:
        """
        if not os.path.exists(self._file_path):
            print('Append Tick, File Not Exist, Cover:{0}'.format(self._file_path))
            record_deep_dir = os.path.dirname(self._file_path)
            if not os.path.exists(record_deep_dir):
                os.makedirs(record_deep_dir)
            return self.write(tick_list, start, length)
        if os.path.getsize(self._file_path) < self.CFileHeaderLen:
            print(f'Append Tick, File Size Error, Cover:{self._file_path}')
            return self.write(tick_list, start, length)
        if (os.path.getsize(self._file_path) - self.CFileHeaderLen) % (self.CTickHeaderLenV1 + self.CTickQuoteLen) != 0:
            print(f'Append Tick, File Layout Error, Cover:{self._file_path}')
            return self.write(tick_list, start, length)
        try:
            # with open(self._file_path, 'rb') as stream:
            #     reader = BinaryReader(stream)
            #     self._read_header(reader)

            with open(self._file_path, 'rb+') as stream:
                count = len(tick_list) - start
                if length < count:
                    count = length

                writer = BinaryWriter(stream)
                stream.seek(0, 2)
                self._write_ticks(tick_list, writer, start, count)

                stream.flush()
            return True

        except Exception as e:
            print("Append Tick Error:{0},{1}".format(self._file_path, str(e)))
        return False
