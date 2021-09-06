# -*- coding: utf-8 -*-
#
#    TypeAtlas Generic Utilities
#    Copyright (C) 2018-2021 Milko Krachounov
#
#    This file is part of TypeAtlas
#
#    TypeAtlas is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    TypeAtlas is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with TypeAtlas.  If not, see <http://www.gnu.org/licenses/>.
#
#                                 ***
#
#    Alternatively, you may use this file (part of TypeAtlas libraries)
#    under the terms of the X11/MIT license as follows:
#
#    Permission is hereby granted, free of charge, to any person
#    obtaining a copy of this software and associated documentation
#    files (the "Software"), to deal in the Software without
#    restriction, including without limitation the rights to use,
#    copy, modify, merge, publish, distribute, sublicense, and/or sell
#    copies of the Software, and to permit persons to whom the
#    Software is furnished to do so, subject to the following
#    conditions:
#
#    The above copyright notice and this permission notice shall be
#    included in all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#    OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#    WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#    OTHER DEALINGS IN THE SOFTWARE.
#

"""Various utility function."""

from collections import OrderedDict
from collections.abc import MutableSet, MutableMapping, Mapping, Hashable
from collections.abc import Set, Sequence
from operator import itemgetter, attrgetter
import re
import os
import io
import sys
import math
import time
import tempfile
import shutil
import fcntl
import errno
import numbers
import collections
import collections.abc
try:
    import typing
except ImportError:
    typing = None


EMPTY_SET = frozenset()


# A style flag to mark text as strike-through
STRIKE = 'strike'


class _GettextStr(str):

    """A decorated string that contains the gettext message ID
    as an attribute.

    FIXME: Qt does not like such strings. it does not display them
    for some reason. Don't forget to complete the translation
    to display."""

    __slots__ = ('gettext_msgid', )


gettext_tag_regex = re.compile(r'^[A-Za-z_]*\|')


def N_(s: str) -> str:

    """Return a translatable string. Any alphabetical prefix before
    before a pipe (e.g. "abc|") is stripped, but a special marked string is
    returned so that _ sends it to gettext.

    Defined here so modules don't have to include langutil to mark for
    translation."""

    match = gettext_tag_regex.search(s)

    if match is not None:
        result = _GettextStr(s[match.end() + 1:])
        result.gettext_msgid = s
        return result

    return s


def U_(s: str) -> str:
    """Do not translate this string or add to gettext, but mark to
    allow easier translation down the line."""
    match = gettext_tag_regex.search(s)
    if match is not None:
        return s[match.end() + 1:]
    return s


_generic_types = {'Tuple': tuple, 'Type': type, 'List': list,
                  'Set': set, 'FrozenSet': frozenset,
                  'DefaultDict': collections.defaultdict,
                  'OrderedDict': collections.OrderedDict,
                  'ChainMap': collections.ChainMap,
                  'Counter': collections.Counter,
                  'Deque': collections.deque,
                  'AbstractSet': collections.abc.Set}


class _FakeGenericType(object):

    __slots__ = ('cls', )

    def __init__(self, cls: type):
        self.cls = cls

    def __getitem__(self, item: type) -> type:
        return self.cls


class _GetattrCallableMeta(type):

    __slots__ = ()

    def __getitem__(self, item: object) -> object:
        return self._getattr(item)


class _FakeLiteralType(object):

    __slots__ = ('cls', )

    def __getitem__(self, item: object) -> type:
        if isinstance(item, tuple):
            if len(set(map(type, item))) == 1:
                return type(item[0])
            return object
        return type(item)


_fakeLiteral = _FakeLiteralType()


# Python breaks backward compatibility with every version
# When I get tired of supporting anything older than Python 3.9
# (which I don't have yet), I will search & replace that out.
if sys.version_info.major == 3 and sys.version_info.minor < 9:
    if typing is None:

        def generic_type(name: str):

            if name in _generic_types:
                return _FakeGenericType(_generic_types[name])
            if name in ['AnyStr', 'Any']:
                return object

            return _FakeGenericType(getattr(collections.abc, name))

    else:
        def generic_type(name: str):
            result = getattr(typing, name, None)
            if result is None:
                if name == 'Literal':
                    return _fakeLiteral
            return result

else:

    def generic_type(name: str):
        if name in _generic_types:
            return _generic_types[name]
        result = getattr(collections.abc, name, None)
        if result is not None:
            return result
        return getattr(typing, name)


Optional = generic_type('Optional')
Callable = generic_type('Callable')
IterableOf = generic_type('Iterable')
Union = generic_type('Union')
Any = generic_type('Any')

Bool = Union[int, bool]

if typing is None or True:
    class Lazy(metaclass=_GetattrCallableMeta):
        """Lazy evaluated type, Lazy[str] is a callable that returns
        string."""
        @classmethod
        def _getattr(cls, t):
            return Callable[..., t]

else:
    T = typing.TypeVar('T')
    class Lazy(Callable[..., T]):
        """Lazy evaluated type, Lazy[str] is a callable that returns
        string."""


class MaybeLazy(metaclass=_GetattrCallableMeta):
    """A variable of a given type, or a function that lazily returns that type.
    MaybeLazy[str] is either a string or a callable that returns str.."""

    @classmethod
    def _getattr(cls, t):
        return Union[t, Lazy[t]]


class MaybeIterable(metaclass=_GetattrCallableMeta):
    """A variable of a given type, or a function that lazily returns that type.
    MaybeLazy[str] is either a string or a callable that returns str.."""

    @classmethod
    def _getattr(cls, t):
        return Union[t, IterableOf[t]]



debug_started = time.time()
debug_last = debug_started

debug_enabled = True
debug_memory = True


def disable_debug():
    """Disable debug."""
    global debug_enabled
    debug_enabled = False


def debugmsg(*args, **kwargs):
    """Display a debug msg. This has the same signature as
    print, except it does not take a file argument."""
    global debug_last
    if not debug_enabled:
        return

    if debug_memory:
        try:
            for line in open('/proc/self/status'):
                if 'VmRSS' not in line:
                    continue
                args = ('[' + ' '.join(line.split()[1:]) + ']', ) + args
                break

        except OSError:
            pass

    now = time.time()
    print("DEBUG %015.9fs [+%015.9fs]" % (
                now - debug_started,
                now - debug_last),
          *args, file=sys.stderr, **kwargs)
    debug_last = now


def infomsg(*args, **kwargs):
    """Display an info msg. This has the same signature as
    print, except it does not take a file argument."""
    print("INFO", *args, file=sys.stderr, **kwargs)

def noticemsg(*args, **kwargs):
    """Display a notice. This has the same signature as
    print, except it does not take a file argument."""
    print("NOTICE", *args, file=sys.stderr, **kwargs)

def bugmsg(*args, **kwargs):
    """We hit a bug. This has the same signature as
    print, except it does not take a file argument."""
    print("BUG", *args, file=sys.stderr, **kwargs)

def warnmsg(*args, **kwargs):
    """Display a warning. This has the same signature as
    print, except it does not take a file argument."""
    print("WARN", *args, file=sys.stderr, **kwargs)

def errmsg(*args, **kwargs):
    """Display an error message This has the same signature as
    print, except it does not take a file argument."""
    print("ERROR", *args, file=sys.stderr, **kwargs)


def debugmsgf(s: str, *args, **kwargs):
    """Display a debug msg with printf() instead of print() signature."""
    debugmsg((s % args) if args else s, **kwargs)

def infomsgf(s, *args, **kwargs):
    """Display an info msg with printf() instead of print() signature."""
    infomsg((s % args) if args else s, **kwargs)

def noticemsgf(s, *args, **kwargs):
    """Display a notice with printf() instead of print() signature."""
    noticemsg((s % args) if args else s, **kwargs)

def bugmsgf(s, *args, **kwargs):
    """Complain about a bug with printf() instead of print() signature."""
    bugmsg((s % args) if args else s, **kwargs)

def warnmsgf(s, *args, **kwargs):
    """Display a warning with printf() instead of print() signature."""
    warnmsg((s % args) if args else s, **kwargs)

def errmsgf(s, *args, **kwargs):
    """Display an error with printf() instead of print() signature."""
    errmsg((s % args) if args else s, **kwargs)


class Struct:

    """A basic object type whose attributes are inherited
    from a dictionary or are freely set"""

    def __init__(self, __d: Mapping, **kwargs):
        vars(self).update(__d, **kwargs)

    @classmethod
    def _bound(cls, d: Mapping) -> 'Struct':
        """Create a struct still connected with a dictionary."""
        self = cls.__new__(cls)
        self.__dict__ = d


class EmptyMapping(Mapping):

    """A new instance of an empty mapping."""

    __slots__ = ()

    def __getitem__(self, key):
        raise KeyError(key)

    def __iter__(self):
        return iter(())

    def __len__(self):
        return 0


class EmptySet(Set):

    """A new instance of an empty set."""

    __slots__ = ()

    def __contains__(self, item):
        return False

    def __iter__(self):
        return iter(())

    def __len__(self):
        return 0


class EmptySequence(Sequence):

    """A new instance of an empty sequence."""

    __slots__ = ()

    def __getitem__(self, key):
        raise KeyError(key)

    def __iter__(self):
        return iter(())

    def __len__(self):
        return 0


#EMPTY_SET = EmptySet()
EMPTY_MAPPING = EmptyMapping()
EMPTY_SEQUENCE = EmptySequence()


def namespace_resolve(namespace: Mapping, attribute: str) -> object:
    """Resolve an attribute in a namespace."""
    return attrgetter(attribute)(Struct._bound(namespace))


class OrderedSet(MutableSet):

    __slots__ = ('_values', )

    def __init__(self, values=()):
        self._values = OrderedDict.fromkeys(values)

    def __contains__(self, value):
        return value in self._values

    def __iter__(self):
        return iter(self._values)

    def __len__(self):
        return len(self._values)

    def __reversed__(self):
        return reversed(self._values)

    def add(self, value):
        self._values[value] = None

    def discard(self, value):
        self._values.pop(value, None)

    def __le__(self, other):
        if isinstance(other, OrderedSet):
            return self._values.keys() <= other._values.keys()
        else:
            return self._values.keys() <= other

    def update(self, values):
        for value in values:
            self.add(value)

    def __repr__(self):
        return '%s(%r)' % (type(self).__name__, list(self._values))


AUTO = object()

size_prefixes = 'kMGTPEZY'


def format_size(size: Optional[numbers.Real],
                unit: str='B', binary: bool=True) -> str:
    """Format the given number representing a size as a string.

    By default, the unit is B (bytes), you can pass a different
    unit.

    By default, binary prefixes are used (KiB vs. KB). You can pass
    binary=False to use SI prefixes. This forces 1000 as a divisor
    instead of 1024.

    None is accepted as size to mean an unknown size.
    """
    if size is None:
        return 'unknown'

    prefixes = iter(size_prefixes)
    prefix = ''

    if binary:
        extra = 'i'
        divisor = 1024
        cutoff = 8192

    else:
        extra = ''
        divisor = 1000
        cutoff = 8000


    while abs(size) >= cutoff:
        try:
            prefix = next(prefixes)
        except StopIteration:
            break
        else:
            size /= divisor

    if not size or isinstance(size, numbers.Integral):
        precision = 0

    else:
        try:
            precision = 3 - int(math.log10(abs(size)))
        except ValueError:
            precision = 3

    if prefix and extra:
        prefix += extra

    precision = max(precision, 0)

    return '%0.*f %s%s' % (precision, size, prefix, unit)


def convert_size_to_bytes(size: numbers.Real, prefix: str='',
                          binary: bool=AUTO) -> numbers.Real:
    """Convert a size with a given prefix (e.g. K) to byte size (or other unit).
    This is used by parse_size().

    The first argument is the size in e.g. kilobytes, the second is the prefix,
    e.g. 'K'. The size in bytes is returned.

    By default, we will detect if the prefix is 'Ki', you can pass binary=True
    or binary=False to force. A multiplier of 1024 will be used for binary prefixes,
    and a multiplier of 1000 for SI prefixes.
    """

    prefixes = size_prefixes.lower()
    prefix = prefix.lower()

    if binary is AUTO:
        binary = prefix.endswith('i')

    if binary:
        prefix.rstrip('i')
    else:
        if prefix.endswith('i'):
            raise ValueError("Invalid SI size %s %s" % (size, prefix))

    if not prefix:
        return size

    n = prefixes.index(prefix) + 1
    divisor = 1024 if binary else 1000

    return size * divisor ** n


def parse_size(size: str, unit: str='B',
               binary: bool=AUTO) -> Union[float, int]:
    """Parse the given human-readable size and return the size as an
    integer (or float) in bytes (or another base unit)

    By default the unit is 'B' (bytes), you can pass a unit of your choosing,
    such as 'Hz'.

    By default, we detect binary (multiplied by 1024) and SI prefix (multiplied
    by 1000). You can pass binary=True or binary=False to force.
    """

    number_pattern = r' -? (?: [0-9]* (?:\.[0-9]*)? | (?:\.[0-9]*)? )'


    match = re.match(r'(?ix) ^ \s* (%s) \s* ([%s]?i?) (?:%s)? \s* $'
                            % (number_pattern,
                               re.escape(size_prefixes),
                               re.escape(unit)), size)

    if not match:
        raise ValueError("Cannot parse size %r" % (size, ))

    size = match.group(1)
    prefix = match.group(2)
    if size.isdigit():
        size = int(size)
    else:
        size = float(size)

    return convert_size_to_bytes(size, prefix, binary=binary)



def isatty(fileno: Union[io.IOBase, int]) -> bool:
    """Return True if the file object or descriptor is a TTY."""
    if not isinstance(fileno, int):
        fileno = fileno.fileno()
    return os.isatty(fileno)


def tty_clear(fileno: Union[io.IOBase, int]) -> str:
    """Return the escape code to clear a TTY."""
    return "\33[2K\r"


def get_umask() -> int:
    """Get the current umask."""

    if True:
        # This version does not have race conditions if nobody
        # changes the umask (which TypeAtlas shouldn't do)
        path = '/proc/%d/status' % (os.getpid(), )
        try:
            with open(path) as f:
                for line in f:
                    parts = line.split()
                    if (len(parts) == 2 and parts[0] == 'Umask:' and
                        parts[1].isdigit() and parts[1][0] == '0'):
                            return int(parts[1], 8)
        except (FileNotFoundError, ValueError) as exc:
            pass

    # This version has race conditions when using threadses
    result = os.umask(0o077)
    os.umask(result)
    return result


class classproperty(object):

    """A class property. A mix of property and classmethod. Does not have
    a setter."""

    def __init__(self, fget, doc=None):
        if doc is None:
            doc = fget.__doc__

        self.fget = fget
        self.__doc__ = doc

    def __get__(self, instance, owner):
        return self.fget(owner)


class Overwriter(object):
    """Overwriter(path, mode='w', buffering=-1, encoding=None,
                        errors=None, newline=None, *,
                        backup=None, keep_perms=True, create_mode=0o666)

    Create a file object that overwrites the file in the specified path.
    It supports only the 'w' and 'wb' modes. The data is written to a
    temporary file, and the original is atomically overwritten on close.
    Should be used as a context manager. If there is an error during
    the write, the file is not overwritten.

    If backup option is given it should be a string specifying the backup
    prefix.

    Example use:
        with Overwriter("hello.txt", 'w', backup='~') as f:
            f.write("Hello World")

    See https://bugs.python.org/issue8604
    See http://bazaar.launchpad.net/~exabyte/blackherd/async-refactor/view/61/blackherd/misc.py#L498
    """

    def __init__(self, path, mode: str='w', *args,
                       backup=None, keep_perms: bool=True,
                       create_mode: int=0o666, **kwargs):
        super().__init__()

        if mode not in ['w', 'wb']:
            raise ValueError("The file needs to be open in write mode")

        if backup is not None:
            if os.sep in backup:
                raise ValueError("Path separator %s not allowed in the backup "
                                 "suffix %s" % (os.sep, backup))
            if os.altsep and os.altsep in backup:
                raise ValueError("Path alternative separator %s not allowed in "
                                 "the backup suffix %s" % (os.altsep, backup))

        if os.path.islink(path):
            path = os.path.realpath(path)
        else:
            path = os.path.abspath(path)

        dirpath, filename = os.path.split(path)

        fd, temppath = tempfile.mkstemp('new', filename, dirpath, mode == 'w')
        try:
            self._file = open(fd, mode, *args, **kwargs)

            self._path = path
            self._temppath = temppath
            self._fd = fd
            self._backup = backup
            self._keep_perms = keep_perms
            self._create_mode = create_mode

        except:
            os.unlink(temppath)
            raise

    @property
    def name(self):
        return self._path

    @property
    def closed(self):
        return self._file.closed

    @property
    def encoding(self):
        return self._file.encoding

    @property
    def errors(self):
        return self._file.errors

    @property
    def softspace(self):
        return self._file.softspace

    @softspace.setter
    def softspace(self, value):
        self._file.softspace = value

    def __enter__(self):
        if self.closed:
            raise ValueError("IO operations unsupported on a closed file")

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.close()
        else:
            self.close(cancel=True)

    def fileno(self):
        return self._file.fileno()

    def readline(self, limit=-1):
        return self._file.readline(limit)

    def readlines(self, hint=None):
        if hint is None:
            return self._file.readlines()
        else:
            return self._file.readlines(hint)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self._file)

    def read(self, size=-1):
        return self._file.read(size)

    def write(self, buf):
        return self._file.write(buf)

    def writelines(self, lines):
        return self._file.writelines(lines)

    def close(self, cancel=False):
        """Closes the file. If cancel is True, the file overwrite is
        cancelled."""
        if self.closed:
            return

        if cancel:
            self._file.close()
            os.unlink(self._temppath)
            return

        if sys.platform == 'win32':
            self._close_windows()
        else:
            self._close_posix()

    def __del__(self):
        self.close(cancel=True)

    def _fsync(self, fd):
        """fsync a file descriptor, calling OS-specific functions
        on platforms that require it (e.g. Mac OS X"""
        if hasattr('os', 'fsync'):
            os.fsync(fd)

        # fsync on Mac OS X doesn't work, it requires using the
        # F_FULLSYNC fcntl
        if hasattr(fcntl, 'F_FULLFSYNC'):
            fcntl.fcntl(fd, fcntl.F_FULLFSYNC)

    def _fsync_path(self, path):
        """Open a path and fsync it (for syncing directories, etc.)"""
        fd = os.open(path, os.O_RDONLY)
        try:
            self._fsync(fd)
        finally:
            os.close(fd)

    def _close_posix(self):
        # Flush the buffers and then call fsync(2) to ensure
        # that the contents of the file have gone to the disk
        # before the atomic rename(2)
        self.flush()
        self._fsync(self._fd)

        self._file.close()

        if self._backup and os.path.exists(self._path):
            backuppath = self._path + self._backup
            try:
                os.unlink(backuppath)
            except EnvironmentError as exc:
                if exc.errno != errno.ENOENT:
                    raise

            # Attempt to create the backup with a link(2), to
            # ensure that the old name will be preserved on
            # failure, and if a hardlink is not possible, copy
            # Catch all possible errors that can result in race
            # conditions that can happen if multiple instances
            # write to the same file, making sure the function
            # completes gracefully.
            try:
                os.link(self._path, backuppath)

            except EnvironmentError as exc:
                if exc.errno in [errno.EPERM, errno.EMLINK, errno.EEXIST]:
                    try:
                        shutil.copy2(self._path, backuppath)
                        self._fsync_path(backuppath)
                    except EnvironmentError as exc:
                        if exc.errno != errno.ENOENT:
                            raise

                elif exc.errno == errno.ENOENT:
                    pass

                else:
                    raise

        if self._keep_perms:
            # That wouldn't preserve ACLs and fancy stuff like that
            if os.path.exists(self._path):
                shutil.copymode(self._path, self._temppath)
            else:
                os.chmod(self._temppath, self._create_mode & ~get_umask())

        os.rename(self._temppath, self._path)
        self._fsync_path(os.path.dirname(self._path))

    def _close_windows(self):
        # Flush the buffers and then call fsync to ensure
        # that the contents of the file have gone to the disk
        # before the rename
        self.flush()
        if hasattr('os', 'fsync'):
            os.fsync(self._fd)

        self._file.close()

        backuppath = None

        if os.path.exists(self._path):
            if self._backup:
                backuppath = self._path + self._backup
            else:
                dirpath, filename = os.path.split(self._path)
                backuppath = tempfile.mktemp('old', filename, dirpath)

            try:
                os.unlink(backuppath)
            except EnvironmentError as exc:
                if exc.errno != errno.ENOENT:
                    raise

            # No atomic rename is supported in Python on Windows, so
            # save the file to a backup name, and remove the backup if
            # the one is not required
            # FIXME: This might lead to race conditions, but I'm not
            # certain how to handle it. Rethink.
            os.rename(self._path, backuppath)

        if self._keep_perms:
            shutil.copymode(self._path, self._temppath)

        os.rename(self._temppath, self._path)
        # self._fsync_path(os.path.dirname(self._path))

        if backuppath and not self._backup:
            if os.path.exists(self._path):
                shutil.copymode(self._path, self._temppath)
            else:
                os.chmod(self._temppath, self._create_mode & ~get_umask())

    def __repr__(self):
        return '<%s for %r at %x>' % (type(self).__name__,
                                      self._file, id(self))

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError("'%s' object has no attribute '%s'" %
                                   (type(self).__name__, name))
        return getattr(self._file, name)

    @property
    def wrapper_object_for(self):
        """Provide the real object to our type checker."""
        return self._file


class DispatchMapProxy(Mapping):
    """Return a proxy to the MethodDispatchMap instance for the
    specified instance and owner. Used to implement the descriptor
    protocol in MethodDispatchMap.

    See http://bazaar.launchpad.net/~exabyte/blackherd/async-refactor/view/61/blackherd/misc.py#L270
    """

    __slots__ = ('_descriptor', '_dict', '_instance', '_owner')

    def __init__(self, descriptor, instance, owner):
        self._descriptor = descriptor
        self._dict = descriptor._dict
        self._instance = instance
        self._owner = owner

    def __getitem__(self, key):
        return descriptor_get(self._dict[key], self._instance, self._owner)

    def __contains__(self, key):
        return key in self._dict

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def get(self, key, default=None):
        try:
            value = self._dict[key]
        except KeyError:
            return default
        else:
            return descriptor_get(value, self._instance, self._owner)

    def __repr__(self):
        return "<%s for %r at %x>" % (type(self).__name__,
                                      self._descriptor, id(self))


class MethodDispatchMap(MutableMapping):
    """Create a dispatch dictionary that can be used to reference
    methods inside a class. It uses the descriptor protocols to
    provide bound methods when indexed on an instance.

        class A(object):
            method_map = MethodDispatchMap()

            @method_map.add('Method1')
            def method1(self):
                pass

            def method2(self):
                self.method_map['Method1']()


    See http://bazaar.launchpad.net/~exabyte/blackherd/async-refactor/view/61/blackherd/misc.py#L309
    """

    __slots__ = ('_dict', )

    def __init__(self, *args, **kwargs):
        super(MethodDispatchMap, self).__init__(*args, **kwargs)
        self._dict = {}

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return DispatchMapProxy(self, instance, owner)

    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, value):
        self._dict[key] = value

    def __delitem__(self, key):
        del self._dict[key]

    def __contains__(self, key):
        return key in self._dict

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __repr__(self):
        return '<%s at %x: %r>' % (type(self).__name__,
                                   id(self), self._dict)

    def copy(self):
        instance = type(self)()
        instance._dict = self._dict.copy()
        return instance

    def add(self, name: Hashable=None) -> Callable:
        """Returns a decorator that would add the function to the dispatch
        dictionary with the specified name as a key. If the name is None,
        the function name would be used.
        """

        def decorator(func):
            if name is None:
                self._dict[func.__name__] = func
            else:
                self._dict[name] = func
            return func
        return decorator

    def get(self, key, default=None):
        """self[k] if key in self else default"""
        return self._dict.get(key, default)

    def clear(self):
        self._dict.clear()


def bytedata_to_int(bytedata: bytes) -> int:
    """Convert a list of byte values (0 to 255) to an integer."""
    return sum(byte * 256 ** i for i, byte in enumerate(reversed(bytedata)))


def sorteddict(d: Mapping, *args,
                  keykey: Union[Callable, bool]=None,
                  valuekey: Union[Callable, bool]=None,
                  **kwargs) -> OrderedDict:
    """Sort the given dictionary and return an OrderedDict.

    Arguments are passed to sorted(). The key= argument accepts
    tuples, you can pass keykey= and valuekey= to just sort by
    key or tuple. You can also just pass keykey=True or valuekey=True
    to just sort by the key or value.
    """
    key = None

    if keykey is not None:
        if valuekey is not None:
            if not callable(keykey):
                if keykey:
                    keykey = lambda s: s
                else:
                    keykey = lambda s: 1
            if not callable(valuekey):
                if valuekey:
                    valuekey = lambda s: s
                else:
                    valuekey = lambda s: 1
            key = lambda tpl: (keykey(tpl[0]), valuekey(tpl[1]))
        else:
            if callable(keykey):
                key = lambda tpl: keykey[tpl[0]]
            elif keykey:
                key = itemgetter(0)

    elif valuekey is not None:
        if callable(valuekey):
            key = lambda tpl: valuekey(tpl[1])
        elif valuekey:
            key = itemgetter(1)

    if key is not None:
        if 'key' in kwargs:
            raise TypeError("two types of sort keys passed")
        kwargs['key'] = key

    return OrderedDict(sorted(d.items(), *args, **kwargs))


def descriptor_get(ob, instance, owner=None):
    """If the object implements the descriptor protocol, try to get the
    attribute for the specified instance and owner. Otherwise, return
    the object.

    If owner is None, type(instance) is used.

    See http://bazaar.launchpad.net/~exabyte/blackherd/async-refactor/view/61/blackherd/misc.py#L248
    """

    if owner is None:
        owner = type(instance)

    # You cannot call type(ob).__get__ because that might be a
    # metaclass method. In theory, ob.__get__ can be an instance method
    # and wrong. However, first, I don't care. Second, the docs say
    # you *can* call descr.__get__() directly [1]. The internal Python
    # implementation seems to call the type, however.
    #
    # [1] https://docs.python.org/3/howto/descriptor.html
    #
    # Here's a fast shortcut to just do it like the docs allow. If
    # it breaks, because of an unlikely situation where the class
    # and the object are both descriptors for some reason, comment
    # or remove the following lines, and uncomment the proper
    # implementation below
    get = getattr(ob, '__get__', None)
    if get is None:
        return ob
    return get(instance, owner)

    ##### Proper implementation of the protocol
    ### for cls in type.mro(type(ob)):
    ###     try:
    ###         get = vars(cls)['__get__']
    ###     except KeyError:
    ###         pass
    ###     else:
    ###         return get(ob, instance, owner)
    ###
    ### return ob

