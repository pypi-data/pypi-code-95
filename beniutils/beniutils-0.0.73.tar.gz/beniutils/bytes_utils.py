import struct

import beniutils as b


class BytesWriter():

    def __init__(self, isBigEndian=True):

        self.isBigEndian = isBigEndian
        self.formatAry = []
        self.valueAry = []

    def toBytes(self):
        formatStr = self.isBigEndian and ">" or "<"
        formatStr += "".join(self.formatAry)
        return struct.pack(formatStr, *self.valueAry)

    def write(self, format, value):
        self.formatAry.append(format)
        self.valueAry.append(value)

    def writeAry(self, func, ary):
        self.writeUInt(len(ary))
        for value in ary:
            func(value)

    # -----

    def writeShort(self, value):
        self.write("h", b.getLimitedValue(value, -32768, 32767))             # int16
        return self

    def writeUShort(self, value):
        self.write("H", b.getLimitedValue(value, 0, 65535))  # int16
        return self

    def writeInt(self, value):
        self.write("i", b.getLimitedValue(value, -2147483648, 2147483647))  # int32
        return self

    def writeUInt(self, value):
        self.write("I", b.getLimitedValue(value, 0, 4294967295))  # int32
        return self

    def writeLong(self, value):
        self.write("q", b.getLimitedValue(value, -9223372036854775808, 9223372036854775807))  # int64
        return self

    def writeULong(self, value):
        self.write("Q", b.getLimitedValue(value, 0, 18446744073709551615))  # int64
        return self

    def writeFloat(self, value):
        self.write("f", value)
        return self

    def writeDouble(self, value):
        self.write("d", value)
        return self

    def writeBool(self, value):
        self.write("?", value)
        return self

    def writeStr(self, value):
        value = value.encode("utf8")
        self.write(f"{len(value)+1}p", value)
        return self

    # -----

    def writeShortAry(self, ary):
        self.writeAry(self.writeShort, ary)
        return self

    def writeUShortAry(self, ary):
        self.writeAry(self.writeUShort, ary)
        return self

    def writeIntAry(self, ary):
        self.writeAry(self.writeInt, ary)
        return self

    def writeUIntAry(self, ary):
        self.writeAry(self.writeUInt, ary)
        return self

    def writeLongAry(self, ary):
        self.writeAry(self.writeLong, ary)
        return self

    def writeULongAry(self, ary):
        self.writeAry(self.writeULong, ary)
        return self

    def writeFloatAry(self, ary):
        self.writeAry(self.writeFloat, ary)
        return self

    def writeDoubleAry(self, ary):
        self.writeAry(self.writeDouble, ary)
        return self

    def writeBoolAry(self, ary):
        self.writeAry(self.writeBool, ary)
        return self

    def writeStrAry(self, ary):
        self.writeAry(self.writeStr, ary)
        return self
