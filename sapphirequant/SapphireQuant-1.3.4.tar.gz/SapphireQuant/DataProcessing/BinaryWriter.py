# -*- coding:utf-8 -*-
"""
Description:
    Binary Writer

Usage:
    from neo.Core.IO.BinaryWriter import BinaryWriter
"""
import sys
import os
import inspect
import struct
import binascii


def swap32(i):
    """
    Change the endianness from little endian to big endian.
    Args:
        i (int):

    Returns:
        int:
    """
    return struct.unpack("<I", struct.pack(">I", i))[0]


def convert_to_u_int160(value):
    """
    Convert an int value to a 10 bytes binary string value.
    Note: the return value is not really 160 bits, nor is it of the neo.Core.UInt160 type

    Args:
        value (int): number to convert.

    Returns:
        str:
    """
    return bin(value + 2 ** 20)[-20:]


def convert_to_u_int256(value):
    """
    Convert an int value to a 16 bytes binary string value.
    Note: the return value is not really 256 bits, nor is it of the neo.Core.UInt256 type

    Args:
        value (int): number to convert.

    Returns:
        str:
    """
    return bin(value + 2 ** 32)[-32:]


class BinaryWriter(object):
    """docstring for BinaryWriter"""

    def __init__(self, stream):
        """
        Create an instance.

        Args:
            stream (BytesIO): a stream to operate on. i.e. a neo.IO.MemoryStream or raw BytesIO.
        """
        super(BinaryWriter, self).__init__()
        self.stream = stream

    def write_byte(self, value):
        """
        Write a single byte to the stream.

        Args:
            value (bytes, str or int): value to write to the stream.
        """
        if type(value) is bytes:
            self.stream.write(value)
        elif type(value) is str:
            self.stream.write(value.encode('utf-8'))
        elif type(value) is int:
            self.stream.write(bytes([value]))
        elif type(value) is bool:
            if value:
                self.stream.write(bytes([1]))
            else:
                self.stream.write(bytes([0]))

    def write_bytes(self, value, unhex=True):
        """
        Write a `bytes` type to the stream.

        Args:
            value (bytes): array of bytes to write to the stream.
            unhex (bool): (Default) True. Set to unhexlify the stream. Use when the bytes are not raw bytes; i.e. b'aabb'

        Returns:
            int: the number of bytes written.
        """
        if unhex:
            try:
                value = binascii.unhexlify(value)
            except binascii.Error:
                pass
        return self.stream.write(value)

    def pack(self, fmt, data):
        """
        Write bytes by packing them according to the provided format `fmt`.
        For more information about the `fmt` format see: https://docs.python.org/3/library/struct.html

        Args:
            fmt (str): format string.
            data (object): the data to write to the raw stream.

        Returns:
            int: the number of bytes written.
        """
        return self.write_bytes(struct.pack(fmt, data), unhex=False)

    def write_char(self, value):
        """
        Write a 1 byte character value to the stream.

        Args:
            value: value to write.

        Returns:
            int: the number of bytes written.
        """
        return self.pack('c', value)

    def write_float(self, value, endian="<"):
        """
        Pack the value as a float and write 4 bytes to the stream.

        Args:
            value (number): the value to write to the stream.
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.

        Returns:
            int: the number of bytes written.
        """
        return self.pack('%sf' % endian, value)

    def write_double(self, value, endian="<"):
        """
        Pack the value as a double and write 8 bytes to the stream.

        Args:
            value (number): the value to write to the stream.
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.

        Returns:
            int: the number of bytes written.
        """
        return self.pack('%sd' % endian, value)

    def write_int8(self, value, endian="<"):
        """
        Pack the value as a signed byte and write 1 byte to the stream.

        Args:
            value:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.

        Returns:
            int: the number of bytes written.
        """
        return self.pack('%sb' % endian, value)

    def write_u_int8(self, value, endian="<"):
        """
        Pack the value as an unsigned byte and write 1 byte to the stream.

        Args:
            value:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.

        Returns:
            int: the number of bytes written.
        """
        return self.pack('%sB' % endian, value)

    def write_bool(self, value):
        """
        Pack the value as a bool and write 1 byte to the stream.

        Args:
            value: the boolean value to write.

        Returns:
            int: the number of bytes written.
        """
        return self.pack('?', value)

    def write_int16(self, value, endian="<"):
        """
        Pack the value as a signed integer and write 2 bytes to the stream.

        Args:
            value:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.

        Returns:
            int: the number of bytes written.
        """
        return self.pack('%sh' % endian, value)

    def write_u_int16(self, value, endian="<"):
        """
        Pack the value as an unsigned integer and write 2 bytes to the stream.

        Args:
            value:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.

        Returns:
            int: the number of bytes written.
        """
        return self.pack('%sH' % endian, value)

    def write_int32(self, value, endian="<"):
        """
        Pack the value as a signed integer and write 4 bytes to the stream.

        Args:
            value:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.

        Returns:
            int: the number of bytes written.
        """
        return self.pack('%si' % endian, value)

    def write_u_int32(self, value, endian="<"):
        """
        Pack the value as an unsigned integer and write 4 bytes to the stream.

        Args:
            value:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.

        Returns:
            int: the number of bytes written.
        """
        return self.pack('%sI' % endian, value)

    def write_int64(self, value, endian="<"):
        """
        Pack the value as a signed integer and write 8 bytes to the stream.

        Args:
            value:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.

        Returns:
            int: the number of bytes written.
        """
        return self.pack('%sq' % endian, value)

    def write_u_int64(self, value, endian="<"):
        """
        Pack the value as an unsigned integer and write 8 bytes to the stream.

        Args:
            value:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.

        Returns:
            int: the number of bytes written.
        """
        return self.pack('%sQ' % endian, value)

    # def write_u_int160(self, value):
    #     """
    #     Write a UInt160 type to the stream.
    #
    #     Args:
    #         value (UInt160):
    #
    #     Raises:
    #         TypeError: when `value` is not of neo.Core.UInt160 type.
    #     """
    #     if type(value) is UInt160:
    #         value.Serialize(self)
    #     else:
    #         raise TypeError("Value must be UInt160 instance.")
    #
    # def WriteUInt256(self, value):
    #     """
    #     Write a UInt256 type to the stream.
    #
    #     Args:
    #         value (UInt256):
    #
    #     Raises:
    #         TypeError: when `value` is not of neo.Core.UInt256 type.
    #     """
    #     if type(value) is UInt256:
    #         value.Serialize(self)
    #     else:
    #         raise TypeError("Value must be UInt256 instance.")

    def write_var_int(self, value, endian="<"):
        """
        Write an integer value in a space saving way to the stream.
        Read more about variable size encoding here: http://docs.neo.org/en-us/node/network-protocol.html#convention

        Args:
            value (int):
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.

        Returns:
            int: the number of bytes written.

        Raises:
            TypeError: if `value` is not of type int.
            ValueError: if `value` is < 0.
        """
        if not isinstance(value, int):
            raise TypeError(f'{value} not int type.')

        if value < 0:
            raise ValueError(f'{value} too small.')

        elif value < 0xfd:
            return self.write_byte(value)

        elif value <= 0xffff:
            self.write_byte(0xfd)
            return self.write_u_int16(value, endian)

        elif value <= 0xFFFFFFFF:
            self.write_byte(0xfe)
            return self.write_u_int32(value, endian)

        else:
            self.write_byte(0xff)
            return self.write_u_int64(value, endian)

    # def write_var_bytes(self, value, endian="<"):
    #     """
    #     Write an integer value in a space saving way to the stream.
    #     Read more about variable size encoding here: http://docs.neo.org/en-us/node/network-protocol.html#convention
    #
    #     Args:
    #         value (bytes):
    #         endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.
    #
    #     Returns:
    #         int: the number of bytes written.
    #     """
    #     length = len(value)
    #     self.write_var_int(length, endian)
    #
    #     return self.write_bytes(value, unhex=False)

    def write_var_string(self, value, encoding="utf-8"):
        """
        Write a string value to the stream.
        Read more about variable size encoding here: http://docs.neo.org/en-us/node/network-protocol.html#convention

        Args:
            value (string): value to write to the stream.
            encoding (str): string encoding format.
        """
        if type(value) is str:
            value = value.encode(encoding)

        length = len(value)
        ba = bytearray(value)
        byts = binascii.hexlify(ba)
        string = byts.decode(encoding)
        self.write_var_int(length)
        self.write_bytes(string)

    def write_fixed_string(self, value, length):
        """
        Write a string value to the stream.

        Args:
            value (str): value to write to the stream.
            length (int): length of the string to write.

        Raises:
            ValueError: if the input `value` length is longer than the fixed `length`
        """
        towrite = value.encode('utf-8')
        slen = len(towrite)
        if slen > length:
            raise ValueError("String '{value}' length is longer than fixed length: {length}")
        self.write_bytes(towrite)
        diff = length - slen

        while diff > 0:
            self.write_byte(0)
            diff -= 1

    # def write_serializable_array(self, array):
    #     """
    #     Write an array of serializable objects to the stream.
    #
    #     Args:
    #         array(list): a list of serializable objects. i.e. extending neo.IO.Mixins.SerializableMixin
    #     """
    #     if array is None:
    #         self.write_byte(0)
    #     else:
    #         self.write_var_int(len(array))
    #         for item in array:
    #             item.Serialize(self)

    def write2000256list(self, arr):
        """
        Write an array of 64 byte items to the stream.

        Args:
            arr (list): a list of 2000 items of 64 bytes in size.
        """
        for item in arr:
            ba = bytearray(binascii.unhexlify(item))
            ba.reverse()
            self.write_bytes(ba)

    # def write_hashes(self, arr):
    #     """
    #     Write an array of hashes to the stream.
    #
    #     Args:
    #         arr (list): a list of 32 byte hashes.
    #     """
    #     length = len(arr)
    #     self.write_var_int(length)
    #     for item in arr:
    #         ba = bytearray(binascii.unhexlify(item))
    #         ba.reverse()
    #         self.write_bytes(ba)

    def write_fixed8(self, value, unsigned=False):
        """
        Write a Fixed8 value to the stream.

        Args:
            value (neo.Fixed8):
            unsigned: (Not used)

        Returns:
            int: the number of bytes written
        """
        #        if unsigned:
        #            return self.write_u_int64(int(value.value))
        return self.write_int64(value.value)
