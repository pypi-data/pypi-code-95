# Copyright (C) 2009-2020 Martin Slouf <martinslouf@users.sourceforge.net>
#
# This file is a part of Summer.
#
# Summer is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

"""Utility functions and classes."""

import datetime
import io
import logging.config
import os.path
import sys
import threading
import typing

from summer.ex import ResourceNotFoundException

logger = logging.getLogger(__name__)


def locate_file(path_to_module: str, filename: str) -> str:
    """Tries to locate the file in *module path*.  Starts the search in
    current directory and goes up in directory structure until file is
    found or module namespace is left.

    Args:

        path_to_module (str): directory path, ususally just pass in
                              ``__file__`` built-in

        filename (str): file to look for

    FIXME martin.slouf -- now it only checks 3 levels up, instead of end of
    module namespace.

    """

    assert path_to_module is not None
    assert filename is not None

    path = os.path.dirname(os.path.abspath(path_to_module))
    for i in range(0, 4):
        path2 = path
        for j in range(0, i):
            path2 = os.path.join(path2, "..")
        path3 = os.path.join(path2, filename)
        logger.debug("trying path %s", path3)
        if os.access(path3, os.R_OK):
            logger.debug("file found: %s", path3)
            return path3
    raise ResourceNotFoundException(path_to_module=path_to_module,
                                    filename=filename)


def chunks(col: typing.Iterable, chunk_size: int):
    """Yield successive n-sized chunks from iterable.

    Thanks to: http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks-in-python

    Args:

        col (collections.Iterable): collection to be chunked

        chunk_size (int): chunk size

    Returns:

        types.GeneratorType: generator over collection of chunks
                             (collection of original elements split into
                             several smaller collections of *chunk_size*
                             length)

    """
    for i in range(0, len(col), chunk_size):
        yield col[i:i + chunk_size]


class Printable(object):
    """Tries to pretty print object properties into a unicode string.

    Suitable for multi-inheritance, see :py:class:`summer.model.Domain`.

    """

    def __str__(self):
        """Return printable object string representation in unicode."""
        tmp = "%s [" % (self.__class__.__name__,)
        for (key, val) in self.__dict__.items():
            tmp += "%s: %s, " % (key, val)
        if len(self.__dict__) > 0:
            tmp = tmp[:-2]
        tmp += "]"
        return tmp

    def __bytes__(self):
        """Return printable object representation in platform specific encoding."""
        encoding = sys.getdefaultencoding()
        return str(self).encode(encoding)

    def __repr__(self):
        return self.__str__()


class FileReader(object):
    """Simple & handy class for reading text file line by line with specified
    encoding.  Converts line read to unicode.  Counts line read.  Does no
    file manipulation (opening, closing) except for reading.  If used, you
    should delegate all reading to this simple class.

    """

    def __init__(self, fin: io.IOBase, enc: str):
        """Creates the :py:class:`FileReader` instance.

        Args:

            fin (io.IOBase): file-like object to be read

            enc (str): file encoding
        """
        self.fin = fin
        self.enc = enc
        self.counter = 0

    def readline(self) -> str:
        """Read single line from a file.

        Returns:

            str: line as unicode string.
        """
        line = self.fin.readline()
        unicode_line = line.decode(self.enc)
        self.counter += 1
        return unicode_line


class ThreadSafeCounter(object):
    """Thread safe counter."""

    def __init__(self, initial_value=0):
        """Creates :py:class:`ThreadSafeCounter` instance.

        Args:

            initial_value (int): initial value

        """
        self.lock = threading.Lock()
        self.counter = initial_value

    def inc(self, increase_by: int = 1) -> int:
        """Increase counter by 1 and return new value."""
        with self.lock:
            self.counter += increase_by
            return self.counter

    def dec(self, decrease_by: int = 1) -> int:
        """Decrease counter by 1 and return new value."""
        with self.lock:
            self.counter -= decrease_by
            return self.counter

    def get(self) -> int:
        with self.lock:
            return self.counter


class IdGenerator(object):
    """Thread safe id generator."""

    def __init__(self):
        self.counter = ThreadSafeCounter(0)

    def gen_id(self) -> int:
        """Generates new id.

        Returns:

            int: new id

        """
        tmp = self.counter.inc()
        logger.info("new id generated %d", tmp)
        return tmp


class Singleton(type):
    """Metaclass that makes the class producing singleton instance."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ConfigValue(object):
    """Configuration class that defines a default value while checking the
    os environment ``os.environ`` for a possible override.
    """

    def __init__(self):
        self.values = dict()

    def __str__(self):
        padding = max([len(env_variable_name) for env_variable_name in self.values.keys()])
        tmp = ""
        for key in sorted(self.values.keys()):
            real_padding = padding - len(key)
            tmp += key + (" " * real_padding) + " = " + str(self.values[key][0]) + "\n"
        return tmp

    def __call__(self, env_variable_name: str, default_value: object) -> object:
        assert isinstance(env_variable_name, str)
        assert default_value is not None
        value = default_value
        target_class = default_value.__class__.__name__
        if env_variable_name in os.environ:
            value_str = os.environ[env_variable_name]
            logger.info("found environment variable %s == %s", env_variable_name, value_str)
            value = self.convert_value_str(value_str, default_value.__class__)
        else:
            logger.info("using default value %s == %s", env_variable_name, value)
        self.values[env_variable_name] = (value, target_class)
        return value

    def convert_value_str(self, value_str: str, target_class: type) -> object:
        """Utility method that converts a string value to proper type

        Args:

            value_str(str): value to be converted

            target_class (type): required target type

        Returns:

            object: Converted value or original one, if no conversion found.
        """
        type_name = target_class.__name__
        if type_name == "int":
            return int(value_str)
        elif type_name == "bool":
            return bool(value_str)
        elif type_name == "datetime.datetime":
            return datetime.datetime.strptime(value_str, "%Y-%m-%d")
        else:
            return value_str
