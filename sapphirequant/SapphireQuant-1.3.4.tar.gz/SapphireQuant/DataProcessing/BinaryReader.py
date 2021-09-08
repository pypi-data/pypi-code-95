"""
Description:
    Binary Reader
Usage:
    from neo.core.IO.BinaryReader import BinaryReader
"""
import sys
import struct
import binascii
import importlib


class BinaryReader(object):
    """docstring for BinaryReader"""

    def __init__(self, stream):
        """
        Create an instance.
        Args:
            stream (BytesIO): a stream to operate on. i.e. a neo.IO.MemoryStream or raw BytesIO.
        """
        super(BinaryReader, self).__init__()
        self.stream = stream

    def unpack(self, fmt, length=1):
        """
        Unpack the stream contents according to the specified format in `fmt`.
        For more information about the `fmt` format see: https://docs.python.org/3/library/struct.html
        Args:
            fmt (str): format string.
            length (int): amount of bytes to read.
        Returns:
            variable: the result according to the specified format.
        """
        return struct.unpack(fmt, self.stream.read(length))[0]

    def read_byte(self, do_ord=True):
        """
        read a single byte.
        Args:
            do_ord (bool): (default True) convert the byte to an ordinal first.
        Returns:
            bytes: a single byte if successful. 0 (int) if an exception occurred.
        """
        try:
            if do_ord:
                return ord(self.stream.read(1))
            return self.stream.read(1)
        except Exception as e:
            print("ord expected character but got none")
        return 0

    def read_bytes(self, length):
        """
        read the specified number of bytes from the stream.
        Args:
            length (int): number of bytes to read.
        Returns:
            bytes: `length` number of bytes.
        """
        value = self.stream.read(length)
        return value

    def safe_read_bytes(self, length):
        """
        read exactly `length` number of bytes from the stream.
        Raises:
            ValueError is not enough data
        Returns:
            bytes: `length` number of bytes
        """
        data = self.read_bytes(length)
        if len(data) < length:
            raise ValueError("Not enough data available")
        else:
            return data

    def read_bool(self):
        """
        read 1 byte as a boolean value from the stream.
        Returns:
            bool:
        """
        return self.unpack('?')

    def read_char(self):
        """
        read 1 byte as a character from the stream.
        Returns:
            str: a single character.
        """
        return self.unpack('c')

    def read_float(self, endian="<"):
        """
        read 4 bytes as a float value from the stream.
        Args:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.
        Returns:
            float:
        """
        return self.unpack("%sf" % endian, 4)

    def read_double(self, endian="<"):
        """
        read 8 bytes as a double value from the stream.
        Args:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.
        Returns:
            float:
        """
        return self.unpack("%sd" % endian, 8)

    def read_int8(self, endian="<"):
        """
        read 1 byte as a signed integer value from the stream.
        Args:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.
        Returns:
            int:
        """
        return self.unpack('%sb' % endian)

    def read_u_int8(self, endian="<"):
        """
        read 1 byte as an unsigned integer value from the stream.
        Args:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.
        Returns:
            int:
        """
        return self.unpack('%sB' % endian)

    def read_int16(self, endian="<"):
        """
        read 2 byte as a signed integer value from the stream.
        Args:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.
        Returns:
            int:
        """
        return self.unpack('%sh' % endian, 2)

    def read_u_int16(self, endian="<"):
        """
        read 2 byte as an unsigned integer value from the stream.
        Args:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.
        Returns:
            int:
        """
        return self.unpack('%sH' % endian, 2)

    def read_int32(self, endian="<"):
        """
        read 4 bytes as a signed integer value from the stream.
        Args:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.
        Returns:
            int:
        """
        return self.unpack('%si' % endian, 4)

    def read_u_int32(self, endian="<"):
        """
        read 4 bytes as an unsigned integer value from the stream.
        Args:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.
        Returns:
            int:
        """
        return self.unpack('%sI' % endian, 4)

    def read_int64(self, endian="<"):
        """
        read 8 bytes as a signed integer value from the stream.
        Args:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.
        Returns:
            int:
        """
        return self.unpack('%sq' % endian, 8)

    def read_u_int64(self, endian="<"):
        """
        read 8 bytes as an unsigned integer value from the stream.
        Args:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.
        Returns:
            int:
        """
        return self.unpack('%sQ' % endian, 8)

    def read_var_int(self, max=sys.maxsize):
        """
        read a variable length integer from the stream.
        The NEO network protocol supports encoded storage for space saving. See: http://docs.neo.org/en-us/node/network-protocol.html#convention
        Args:
            max (int): (Optional) maximum number of bytes to read.
        Returns:
            int:
        """
        fb = self.read_byte()
        if fb == 0:
            return fb
        value = 0
        if hex(fb) == '0xfd':
            value = self.read_u_int16()
        elif hex(fb) == '0xfe':
            value = self.read_u_int32()
        elif hex(fb) == '0xff':
            value = self.read_u_int64()
        else:
            value = fb

        if value > max:
            raise Exception("Invalid format")

        return int(value)

    def read_var_bytes(self, max=sys.maxsize):
        """
        read a variable length of bytes from the stream.
        The NEO network protocol supports encoded storage for space saving. See: http://docs.neo.org/en-us/node/network-protocol.html#convention
        Args:
            max (int): (Optional) maximum number of bytes to read.
        Returns:
            bytes:
        """
        length = self.read_var_int(max)
        return self.read_bytes(length)

    def read_string(self):
        """
        read a string from the stream.
        Returns:
            str:
        """
        length = self.read_u_int8()
        return self.unpack(str(length) + 's', length)

    def read_var_string(self, max=sys.maxsize):
        """
        Similar to `read_string` but expects a variable length indicator instead of the fixed 1 byte indicator.
        Args:
            max (int): (Optional) maximum number of bytes to read.
        Returns:
            bytes:
        """
        length = self.read_var_int(max)
        return self.unpack(str(length) + 's', length)

    def read_fixed_string(self, length):
        """
        read a fixed length string from the stream.
        Args:
            length (int): length of string to read.
        Returns:
            bytes:
        """
        return self.read_bytes(length).rstrip(b'\x00')

    def read_serializable_array(self, class_name, max=sys.maxsize):
        """
        Deserialize a stream into the object specific by `class_name`.
        Args:
            class_name (str): a full path to the class to be deserialized into. e.g. 'neo.Core.Block.Block'
            max (int): (Optional) maximum number of bytes to read.
        Returns:
            list: list of `class_name` objects deserialized from the stream.
        """
        module = '.'.join(class_name.split('.')[:-1])
        klassname = class_name.split('.')[-1]
        klass = getattr(importlib.import_module(module), klassname)
        length = self.read_var_int(max=max)
        items = []
        #        logger.info("READING ITEM %s %s " % (length, class_name))
        try:
            for i in range(0, length):
                item = klass()
                item.Deserialize(self)
                #                logger.info("deserialized item %s %s " % ( i, item))
                items.append(item)
        except Exception as e:
            print("Couldn't deserialize %s " % e)

        return items

    def read2000256_list(self):
        """
        read 2000 times a 64 byte value from the stream.
        Returns:
            list: a list containing 2000 64 byte values in reversed form.
        """
        items = []
        for i in range(0, 2000):
            data = self.read_bytes(64)
            ba = bytearray(binascii.unhexlify(data))
            ba.reverse()
            items.append(ba.hex().encode('utf-8'))
        return items

    def read_hashes(self):
        """
        read Hash values from the stream.
        Returns:
            list: a list of hash values. Each value is of the bytearray type.
        """
        len = self.read_var_int()
        items = []
        for i in range(0, len):
            ba = bytearray(self.read_bytes(32))
            ba.reverse()
            items.append(ba.hex())
        return items
