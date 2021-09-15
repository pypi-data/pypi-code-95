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
            return "\033[1;36m{:>2.1f}\033[0m TB".format(byteval / 2**40)
        elif byteval / 2**30 >= 1:
            return "\033[1;35m{:>2.1f}\033[0m GB".format(byteval / 2**30)
        elif byteval / 2**20 >= 1:
            return "\033[1;32m{:>2.1f}\033[0m MB".format(byteval / 2**20)
        elif byteval / 2**10 >= 1:
            return "\033[33m{:>2.1f}\033[0m KB".format(byteval / 2**10)
        else:
            return "\033[1;31m{:>3.0f}\033[0m B".format(byteval)
