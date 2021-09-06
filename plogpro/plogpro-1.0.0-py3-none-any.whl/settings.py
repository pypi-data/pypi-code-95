from enum               import Enum
from collections.abc    import Mapping
from functools          import total_ordering


@total_ordering
class LogType(Enum):
    """An enumeration for indicating the severity of a log message

    Attributes:
        DEBUG
            Useful information for debugging only
        INFO
            General information
        WARNING
            A warning to the user
        ERROR
            Information about an error that has occurred
        FATAL
            Information about an error that resulted in a crash
    """
    DEBUG   = 1
    INFO    = 2
    WARNING = 3
    ERROR   = 4
    FATAL   = 5

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        raise NotImplementedError


@total_ordering
class ReleaseType(Enum):
    """An enumeration for indicating the state of the software using Plogpro

    Attributes:
        DEBUG
            Everything is enabled and as verbose as possible
        VERBOSE
            Debugging log messages (``LogType.DEBUG``) are disabled, but other
            messages will still be shown and profilers still work
        RELEASE
            Only log messages indicating an error (``LogType.ERROR`` or higher)
            are shown and profilers are disabled
        RELEASE_QUIET
            All loggers and profilers are disabled
    """
    DEBUG         = 1
    VERBOSE       = 2
    RELEASE       = 3
    RELEASE_QUIET = 4

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        raise NotImplementedError


class Config(Mapping):
    """A dict-like object that contains the settings for Plogpro

    This class is a singleton, which means that every instance contains the same
    info and changes to any instance will also apply to every other instance.
    Use the standard instance ``config`` to avoid any confusion.

    Settings can be accessed using square brackets, e.g.::

        print(config['release'])

    will print the type of release to the console. To change a setting, use the
    same syntax::

        config['release'] = ReleaseType.DEBUG

    will change the release type to ``DEBUG``, which is the most verbose type.
    The list of attributes below shows the possible cofiguration settings.

    Warning:
        Only change the settings at the beginning of your program. Changing the
        settings in a later stage can result in unexpected errors. For example,
        the ``setup()`` or ``teardown()`` methods that are available in most
        base classes will not be called if
        ``config['release'] == ReleaseType.RELEASE_QUIET``, therefore a file
        that needs to be opened and closed in those methods will not be
        available is the type of release changes from
        ``ReleaseType.RELEASE_QUIET`` to a more verbose type after creating e.g.
        a logger or profiler.

    Attributes:
        release (ReleaseType)
            The state of the software that uses Plogpro
    """

    # Default configurations
    _defaults = {
        "release": ReleaseType.DEBUG,
    }

    # Override __new__ to make this class a singleton
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    # Set default settings
    def __init__(self):
        self._store = self._defaults

    def __getitem__(self, key):
        return self._store[key]

    # Only allow changing valid keys
    def __setitem__(self, key, value):
        if key not in self._defaults.keys():
            raise KeyError
        if type(key) != type(self._defaults[key]):
            raise ValueError("A value of type {} is expected for the setting '{}', but got type {}.".format(
                type(self._defaults[key]), key, type(key)))
        self._store[key] = value

    # Don't allow deleting items
    def __delitem__(self, key):
        pass

    def __iter__(self):
        return iter(self._store)

    def __len__(self):
        return len(self._store)

config = Config()
