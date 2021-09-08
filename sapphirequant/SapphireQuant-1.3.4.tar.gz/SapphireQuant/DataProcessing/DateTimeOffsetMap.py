import datetime

from SapphireQuant.Core.CSharpUtils import CSharpUtils


class OffsetCount:
    """
    偏移量和个数
    """
    def __init__(self, offset, count):
        self._offset = offset
        self._count = count

    @property
    def offset(self):
        """
        偏移量
        :return:
        """
        return self._offset

    @property
    def count(self):
        """
        个数
        :return:
        """
        return self._count

    def to_string(self):
        """

        :return:
        """
        msg = 'offset:' + str(self._offset)
        msg += 'count:' + str(self._count)
        return msg


class DateTimeOffsetMap:
    """
    时间索引
    """
    def __init__(self, file_header):
        self._bucket_size = 32
        self._mask = self._bucket_size - 1
        self._default_key = datetime.datetime(2999, 1, 1)
        self._keys = []
        self._values = []
        for i in range(32):
            self._keys.append(datetime.datetime(2999, 1, 1))
            self._values.append(OffsetCount(999999, 0))
        self._file_header = file_header

    def add(self, date_time, offset):
        """
        添加
        :param date_time:
        :param offset:
        """
        if date_time == self._default_key:
            raise Exception('Invalid Date Time')

        key = datetime.datetime(date_time.year, date_time.month, date_time.day)
        key_hash = self.hash_key(key)
        index = key_hash & self._mask  # _mask二进制0b11111,这里为了保证index在1-31
        found = False
        old_index = index
        while self._keys[index] != self._default_key:
            if self._keys[index] == key:
                found = True
                break

            key_hash += 1
            index = key_hash & self._mask
            if old_index == index:
                raise Exception("Unexpected Collision Is Detected In DateTimeOffsetMap")

        if found:
            old = self._values[index]
            self._values[index] = OffsetCount(old.offset, old.count + 1)
        else:
            self._keys[index] = key
            self._values[index] = OffsetCount(offset, 1)
            self._file_header.mark_as_dirty(True)

        return not found

    def reset_count(self, date_time):
        if date_time == self._default_key:
            raise Exception('Invalid Date Time')

        key = datetime.datetime(date_time.year, date_time.month, date_time.day)
        key_hash = self.hash_key(key)
        index = key_hash & self._mask  # _mask二进制0b11111,这里为了保证index在1-31
        found = False
        old_index = index
        while self._keys[index] != self._default_key:
            if self._keys[index] == key:
                found = True
                break

            key_hash += 1
            index = key_hash & self._mask
            if old_index == index:
                raise Exception("Unexpected Collision Is Detected In DateTimeOffsetMap")

        if found:
            old = self._values[index]
            self._values[index] = OffsetCount(old.offset, 0)

    def get_count(self):
        count = 0
        for data in self._values:
            count += data.count
        return count

    def get_trading_day_offsets(self, begin_trading_day, end_trading_day):
        """

        :param begin_trading_day:
        :param end_trading_day:
        :return:
        """
        start = begin_trading_day
        end = end_trading_day
        while True:
            data = self.try_get(start)
            if data[0]:
                start_offset = data[1]
                start_count = data[2]
                break
            start = start + datetime.timedelta(days=1)
            if start > end_trading_day:
                start_offset = -1
                end_offset = -1
                start_count = 0
                end_count = 0
                return False, start_offset, end_offset, start_count, end_count

        while True:
            data = self.try_get(end)
            if data[0]:
                end_offset = data[1]
                end_count = data[2]
                break
            end = end + datetime.timedelta(days=-1)
            if end < begin_trading_day:
                start_offset = -1
                end_offset = -1
                start_count = 0
                end_count = 0
                return False, start_offset, end_offset, start_count, end_count

        return start_offset <= end_offset, start_offset, end_offset, start_count, end_count

    def get_start_offset(self, key):
        """

        :param key:
        :return:
        """
        if key == self._default_key:
            raise Exception("Invalid Date Time")

        key = datetime.datetime(key.year, key.month, key.day)
        temp_key = self._default_key
        index = -1

        key_hash = self.hash_key(key)
        idx = key_hash & self._mask
        for i in range(0, self._bucket_size):
            if self._keys[idx] != self._default_key:
                if key == self._keys[idx]:
                    index = idx
                    break

                if key < self._keys[idx]:
                    if (temp_key == self._default_key) | (temp_key > self._keys[idx]):
                        temp_key = self._keys[idx]
                        index = idx

            idx += 1
            if idx == len(self._keys):
                idx = 0

        if index == -1:
            raise Exception("Invalid Date Time")

        value = self._values[index]
        offset = value.offset
        count = value.count
        return offset, count

    def get_end_offset(self, key):
        """

        :param key:
        :return:
        """
        if key == self._default_key:
            raise Exception("Invalid Date Time")

        key = datetime.datetime(key.year, key.month, key.day)
        temp_key = self._default_key
        index = -1

        key_hash = self.hash_key(key)
        idx = key_hash & self._mask
        for i in range(0, self._bucket_size):
            if self._keys[idx] != self._default_key:
                if key == self._keys[idx]:
                    index = idx
                    break

                if key > self._keys[idx]:
                    if (temp_key == self._default_key) or (temp_key < self._keys[idx]):
                        temp_key = self._keys[idx]
                        index = idx

            idx += 1
            if idx == len(self._keys):
                idx = 0

        if index == -1:
            raise Exception("Invalid Date Time")

        value = self._values[index]
        offset = value.offset
        count = value.count
        return offset, count

    def try_get(self, key):
        """

        :param key:
        :return:
        """
        if key == self._default_key:
            raise Exception("invalid date time")

        key = datetime.datetime(key.year, key.month, key.day)
        key_hash = self.hash_key(key)
        index = key_hash & self._mask  # _mask二进制0b11111,这里为了保证index在1-31
        found = False
        old_index = index
        while self._keys[index] != self._default_key:
            if self._keys[index] == key:
                found = True
                break

            key_hash += 1
            index = key_hash & self._mask
            if old_index == index:
                raise Exception("Unexpected Collision Is Detected In DateTimeOffsetMap")

        if found:
            value = self._values[index]
            offset = value.offset
            count = value.count
        else:
            offset = -1
            count = 0

        return found, offset, count

    def write(self, writer):
        """

        :param writer:
        """
        for i in range(0, self._bucket_size):
            writer.write_int64(CSharpUtils.get_c_sharp_ticks(self._keys[i]))
        for i in range(0, self._bucket_size):
            value = self._values[i]
            writer.write_int64(value.offset)
            writer.write_int32(value.count)

    def read(self, reader):
        """

        :param reader:
        """
        self._keys = []
        for i in range(0, self._bucket_size):
            self._keys.append(CSharpUtils.convert_c_sharp_ticks_to_py_date_time(reader.read_int64()))

        self._values = []
        for i in range(0, self._bucket_size):
            self._values.append(OffsetCount(reader.read_int64(), reader.read_int32()))

    @staticmethod
    def hash_key(time):
        """

        :param time:
        :return:
        """
        return time.day
