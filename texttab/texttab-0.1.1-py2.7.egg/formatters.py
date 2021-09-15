"""
Formatter classes that can be applied to columns
"""


class ColumnFormatter(object):
    def __init__(self):
        return

    def format(self, value):
        raise NotImplemented


class ReadableBytesFormatter(ColumnFormatter):
    def __init__(self, suffix="b"):
        super(ReadableBytesFormatter, self).__init__()
        self.suffix = suffix

    def format(self, value):
        return self.human_readable_bytes(value)

    def human_readable_bytes(self, byteval):
        if byteval / 2**40 >= 1:
            return "{:>2.1f} T{} ".format(byteval / 2**40, self.suffix)
        elif byteval / 2**30 >= 1:
            return "{:>2.1f} G{} ".format(byteval / 2**30, self.suffix)
        elif byteval / 2**20 >= 1:
            return "{:>2.1f} M{} ".format(byteval / 2**20, self.suffix)
        elif byteval / 2**10 >= 1:
            return "{:>2.1f} K{} ".format(byteval / 2**10, self.suffix)
        else:
            return "{:>3.0f}  {} ".format(byteval, self.suffix)


class UnixPermissionsFormatter(ColumnFormatter):
    def __init__(self):
        super(UnixPermissionsFormatter, self).__init__()

    def format(self, value):
        d = {
            0: '---',
            1: '--x',
            2: '-w-',
            3: '-wx',
            4: 'r--',
            5: 'r-x',
            6: 'rw-',
            7: 'rwx',
        }
        mode_char = "-"
        ret_str = "{}{}{}{}".format(
            mode_char,
            d[(value & 0700) >> 6],
            d[(value & 0070) >> 3],
            d[value & 0007]
        )
        return ret_str
