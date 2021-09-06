from abc        import ABCMeta, abstractmethod
from datetime   import datetime

from .settings  import config, LogType, ReleaseType


class LogMessage:
    """Container class for log messages

    This class contains all the necessary information about a log message and is
    used to send this information from the base class ``Logger`` to an actual
    implementation of a logger. More specifically, when a user calls the
    ``log()`` method of a logger, a ``LogMessage`` will be created and passed on
    to the ``write_message()`` implementation.

    Arguments:
        msg (str)
            The message
        msg_type (LogType, optional)
            The message type that indicates its severity, this should be one
            of the options given by the enumeration ``LogType``
            (default: ``LogType.INFO``)

    Attributes:
        msg (str)
            The text message given to the ``log()`` function
        type (LogType)
            The type of the log message
        time (datetime)
            The time of the log message
        timestring (str)
            A formatted string with the date and time of the message
    """

    def __init__(self, msg, msg_type):
        if not isinstance(msg, str):
            raise ValueError("The given message is not a string.")
        if not isinstance(msg_type, LogType):
            raise ValueError("The message type is not an instance of the enum \"Type\".")

        self.msg = msg
        self.type = msg_type
        self.time = datetime.now()
        self.timestring = self.time.strftime("%d/%m/%Y %H:%M:%S")


class Logger(metaclass=ABCMeta):
    """Base class that provides an interface for different loggers

    To be able to log messages using a logger of your choice, e.g.
    ``TextLogger``, create an instance of that logger. You can then use the
    method ``log(msg, msg_type)`` to actually write a log message to a file.

    To implement a new logger, create a class that inherits from ``Logger`` and
    at least has a method ``write_message(self, msg)`` that accepts one
    argument: an instance of the ``LogMessage`` class. If you need to do
    anything once in the beginning or the and, you can override the ``setup()``
    and/or ``teardown()`` methods respectively.

    Warning:
        The ``log()`` method should **not** be overwritten.
    """

    def __init__(self):
        if config["release"] < ReleaseType.RELEASE_QUIET:
            self.setup()

    def __del__(self):
        if config["release"] < ReleaseType.RELEASE_QUIET:
            self.teardown()

    def setup(self):
        pass

    def teardown(self):
        pass

    def log(self, msg, msg_type=LogType.INFO):
        """Write a log message

        Arguments:
            msg (str)
                The message
            msg_type (LogType, optional)
                The message type that indicates its severity, this should be one
                of the options given by the enumeration ``LogType``
                (default: ``LogType.INFO``)
        """
        if ((config["release"] == ReleaseType.RELEASE_QUIET) or
                (config["release"] == ReleaseType.RELEASE and msg_type >= LogType.ERROR) or
                (config["release"] == ReleaseType.VERBOSE and msg_type >= LogType.INFO)):
            return
        message = LogMessage(msg, msg_type)
        self.write_message(message)

    @abstractmethod
    def write_message(self, msg):
        raise NotImplementedError
