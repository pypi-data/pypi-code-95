"""
"""
__version__ = "1.0.2"

# Standard Library
import os
import sys
from io import StringIO
from functools import wraps
from contextlib import contextmanager
from collections import namedtuple

# Third-Party
import colorama

# File Descriptors
STDIN_FD = 0
STDOUT_FD = 1
STDERR_FD = 2


class Stream(object):
    """Coloured text stream in C++ style with verbosity control.

    Example
    -------
    >>> Stream.set_lvl(0)
    >>> mystream = Stream()
    >>> mystream[1] << "Hello."
    >>> mystream[0] << "Hello."
    Hello.
    >>> mystream << "Hello."
    Hello.
    """

    COLORS = {
        "BLACK",
        "RED",
        "GREEN",
        "YELLOW",
        "BLUE",
        "MAGENTA",
        "CYAN",
        "WHITE",
        None,
    }
    STYLES = {"DIM", "NORMAL", "BRIGHT", None}

    RESET = colorama.Style.RESET_ALL

    Params = namedtuple(
        "params", ["bg", "fg", "sty", "file"], defaults=[None, None, None, sys.stdout]
    )

    __ref__ = {}
    __lvl__ = None

    def __new__(cls, lvl: int = 0, **kwargs: dict):
        ## Gather parameters
        params = cls.Params(**kwargs)

        ## Check Background
        if params.bg not in cls.COLORS:
            raise ValueError(f"Color {params.bg} not available.\nOptions: {cls.COLORS}")
        ## Check Foreground
        if params.fg not in cls.COLORS:
            raise ValueError(f"Color {params.fg} not available.\nOptions: {cls.COLORS}")
        ## Check Style
        if params.sty not in cls.STYLES:
            raise ValueError(
                f"Style {params.sty} not available.\nOptions: {cls.STYLES}"
            )

        if params not in cls.__ref__:
            cls.__ref__[params] = super().__new__(cls)
        return cls.__ref__[params]

    def __init__(self, lvl: int = 0, **kwargs: dict):
        """
        Parameters
        ----------
        lvl : int
            Verbosity level.
        **kwargs
            bg : str
                Background ANSI control sequence.
            fg : str
                Foreground ANSI control sequence.
            sty : str
                Style ANSI control sequence.
            file : _io.TextIOWrapper
                File object interface for writing to.
        """

        ## Set lvl
        self.lvl = lvl

        ## Gather parameters
        bg, fg, sty, file = self.params = self.Params(**kwargs)

        ## Gather escape sequences
        self.bg = "" if bg is None else getattr(colorama.Back, bg)
        self.fg = "" if fg is None else getattr(colorama.Fore, fg)
        self.sty = "" if sty is None else getattr(colorama.Style, sty)

        ## Set output file
        self.file = file

    def __repr__(self):
        params = ", ".join(
            [f"{key}={getattr(self.params, key)!r}" for key in ("bg", "fg", "sty")]
        )
        return f"{self.__class__.__name__}({self.lvl}, {params})"

    def printf(self, *args, **kwargs) -> int:
        """"""
        if self.echo:
            return self._printf(*args, **kwargs)
        else:
            return 0

    def _printf(self, *args, **kwargs):
        """"""
        print(self.bg, self.fg, self.sty, sep="", end="", file=self.file)
        print(*args, **kwargs, file=self.file)
        print(self.RESET, sep="", end="", file=self.file)

    def string(self, s: str):
        """Generates formated string, appending and preppending respective ANSI control sequences.

        Parameters
        ----------
        s : str
            Input string.

        Returns
        -------
        str
            Formated string.
        """
        if self.bg or self.fg or self.sty:
            return f"{self.RESET}{self.bg}{self.fg}{self.sty}{s}{self.RESET}"
        else:
            return s

    def __lshift__(self, s: str):
        if self.echo:
            print(self.string(s), file=self.file)
        return self

    def __getitem__(self, lvl: int):
        return self.__class__(lvl, **self.params._asdict())

    def __call__(self, **kwargs):
        return self.__class__(self.lvl, **kwargs)

    def __bool__(self) -> bool:
        return self.echo

    ## Block skip
    class SkipBlock(Exception):
        ...

    def trace(self, *args, **kwargs):
        raise self.SkipBlock()

    def __enter__(self):
        """Implements with-block skipping."""
        if not self.echo:
            sys.settrace(lambda *args, **kwargs: None)
            frame = sys._getframe(1)
            frame.f_trace = self.trace
        else:
            return self

    def __exit__(self, type_, value, traceback):
        """"""
        if type_ is None:
            return None
        elif issubclass(type_, self.SkipBlock):
            return True
        else:
            return None

    ## File interface
    def read(self):
        raise OSError("Can't read from this stream.")

    def write(self, s: str) -> int:
        return self.printf(s)

    @property
    def echo(self):
        return (self.__lvl__ is None) or (self.__lvl__ >= self.lvl)

    @classmethod
    def set_lvl(cls, lvl: int = None):
        if lvl is None or type(lvl) is int:
            cls.__lvl__ = lvl
        else:
            raise TypeError(
                f"Invalid type `{type(lvl)}`` for debug lvl. Must be `int`."
            )

class StringStream(Stream):
    
    @wraps(Stream.__init__)
    def __init__(self, *args, **kwargs):
        Stream.__init__(self, *args, **kwargs)
        self._string_io = StringIO()

    def __lshift__(self, s: str):
        if self.echo:
            print(self.string(s), file=self._string_io)
        return self

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        return None

    def read(self) -> str:
        return self._string_io.getvalue()

    def write(self, s: str):
        return self._string_io.write(s)

class NullStream(object):
    """Redirects both sys.stdout and sys.stderr to os.devnull."""

    __ref__ = None

    def __new__(cls):
        if cls.__ref__ is None:
            cls.__ref__ = object.__new__(cls)
        return cls.__ref__

    def __enter__(self, *args, **kwargs):
        global sys
        self.sys_stderr = sys.stderr
        self.sys_stdout = sys.stdout
        sys.stderr = sys.stdout = open(os.devnull, "w")
        return self

    def __exit__(self, *args, **kwargs):
        global sys
        if not sys.stdout.closed:
            sys.stdout.close()
        if not sys.stderr.closed:
            sys.stderr.close()
        sys.stdout = self.sys_stdout
        sys.stderr = self.sys_stderr
        return None

    def read(self) -> str:
        raise OSError("Can't read from this stream.")


    def write(self, s: str) -> int:
        return 0

class logfile:
    """Duplicates STDERR file descriptor"""

    def __init__(self):
        self.fd = os.dup(STDERR_FD)
        self.file = os.fdopen(self.fd, mode="w", encoding="utf-8")

    def write(self, s: str) -> int:
        return self.file.write(s)

@contextmanager
def redirect_stderr(target):
    """
    """
    global sys
    sys_stderr = sys.stderr
    try:
        sys.stderr = target
        yield target
    finally:
        sys.stderr = sys_stderr
        return

@contextmanager
def redirect_stdout(target):
    """
    """
    global sys
    sys_stdout = sys.stdout
    try:
        sys.stdout = target
        yield target
    finally:
        sys.stdout = sys_stdout
        return


## Initialize shell environment
colorama.init()
os.system("")

## Create default streams
stderr = Stream(fg="RED", file=sys.stderr)
stdwar = Stream(fg="YELLOW", file=sys.stderr)
stdlog = Stream(fg="CYAN", file=logfile())  ## Initialize log file
stdout = Stream(file=sys.stdout)
devnull = NullStream()

## Output
__all__ = ["Stream", "StringStream", "redirect_stdout", "redirect_stderr", "stderr", "stdwar", "stdlog", "devnull"]