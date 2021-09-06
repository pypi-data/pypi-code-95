from __future__ import print_function
from .logger    import *


class TextLogger(Logger):
    """A logger that writes messages to a text file

    The messages are written with the following syntax::

        [  <Type>  ] <Date> <Time> - <Message>

    Arguments:
        fname (str)
            The name of the output file
        overwrite (bool, optional)
            Whether to overwrite the contents of the output file if it
            already exists or to append the messages to the end of the file
            (default: `False`)
    """

    def __init__(self, fname, overwrite=False):
        self.fname = fname
        self.overwrite = overwrite
        super().__init__()

    def setup(self):
        self.file = open(self.fname, 'w' if self.overwrite else 'a')

    def teardown(self):
        self.file.close()

    def write_message(self, msg):
        output_string  = "[" + msg.type.name.center(10) + "] "
        output_string += msg.timestring + " - " + msg.msg
        self.file.write(output_string + '\n')


class ConsoleLogger(Logger):
    """A logger that writes messages to the console

    The messages are written with the following syntax::

        [  <Type>  ] <Date> <Time> - <Message>
    """

    def write_message(self, msg):
        output_string  = "[" + msg.type.name.center(10) + "] "
        output_string += msg.timestring + " - " + msg.msg
        print(output_string)
