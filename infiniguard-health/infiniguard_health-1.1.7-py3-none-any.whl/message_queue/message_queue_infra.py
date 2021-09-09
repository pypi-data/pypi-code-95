""" A simple messaging queue"""

from functools import wraps
from collections import defaultdict, Counter

from infiniguard_health.utils import Singleton

VALIDATE_NEW_SYSTEM_STATE_MESSAGE = 'validate_new_system_state'


class MessageDoesntExist(Exception):
    """ Raised when trying remove a message that doesn't exist. """
    pass


# The message queue should be a singelton, and only created by this package.
# In order to use it, import message_queue from the package.
class MessageQueue(metaclass=Singleton):
    __slots__ = ('_messages',)

    def __init__(self):
        """ Creates new MessageQueue object. """
        self._messages = defaultdict(set)

    def __repr__(self):
        """ Returns MessageBus string representation.

        :return: Instance with how many subscribed messages.
        """
        return "<{}: {} subscribed messages>".format(
            self.__class__.__name__,
            self.message_count
        )

    def __str__(self):
        """ Returns MessageBus string representation.

        :return: Instance with how many subscribed messages.
        """

        return "{}".format(self.__class__.__name__)

    @property
    def message_count(self):
        """ Sugar for returning total subscribed messages.

        :return: Total amount of subscribed messages.
        :rtype: int
        """
        return self._subscribed_message_count()

    def subscribe_to(self, message):
        """ Decorator for subscribing a function to a specific message.

        :param message: Name of the message to subscribe to.
        :type message: str

        :return: The outer function.
        :rtype: Callable
        """
        def outer(func):
            self.add_function_to_message(func, message)

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return outer

    def add_function_to_message(self, func, message):
        """ Adds a function to a message.

        :param func: The function to call when message is emitted
        :type func: Callable

        :param message: Name of the message.
        :type message: str
        """
        self._messages[message].add(func)

    def dispatch_message(self, message, *args, **kwargs):
        """ Dispatch a message and run the subscribed functions.

        :param message: Name of the message.
        :type message: str

        .. notes:
            Passing in threads=True as a kwarg allows to run emitted messages
            as separate threads. This can significantly speed up code execution
            depending on the code being executed.
        """
        for func in self._message_funcs(message):
            func(*args, **kwargs)

    def dispatch_message_for_specific_functions(self, message, func_names, *args, **kwargs):
        """ Runs functions subscribed on the given message, out of the given list of functions.

        :param message: Name of the message.
        :type message: str

        :param func_names: Function(s) to emit.
        :type func_names: Union[ str | List[str] ]
        """
        if isinstance(func_names, str):
            func_names = [func_names]

        for func in self._message_funcs(message):
            if func.__name__ in func_names:
                func(*args, **kwargs)

    def dispatch_after_function(self, message):
        """ Decorator that dispatches the message after the decorated function is completed.

        :param message: Name of the message.
        :type message: str

        :return: Callable

        .. note:
            This plainly just calls functions without passing params into the
            subscribed callables.
        """

        def outer(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                returned = func(*args, **kwargs)
                self.dispatch_message(message)
                return returned

            return wrapper

        return outer

    def remove_message(self, func_name, message):
        """ Removes a subscribed function from a specific message.

        :param func_name: The name of the function to be removed.
        :type func_name: str

        :param message: The name of the message.
        :type message: str

        :raise MessageDoesntExist if there func_name doesn't exist in message.
        """
        message_funcs_copy = self._messages[message].copy()

        for func in self._message_funcs(message):
            if func.__name__ == func_name:
                message_funcs_copy.remove(func)

        if self._messages[message] == message_funcs_copy:
            err_msg = "function doesn't exist inside message {} ".format(message)
            raise MessageDoesntExist(err_msg)
        else:
            self._messages[message] = message_funcs_copy

    def inspect(self):
        """ Return all messages and subscribers"""
        return self._messages

    def _message_funcs(self, message):
        """ Returns an Iterable of the functions subscribed to a message.

        :param message: Name of the message.
        :type message: str

        :return: A iterable to do things with.
        :rtype: Iterable
        """
        for func in self._messages[message]:
            yield func

    def _message_func_names(self, message):
        """ Returns string name of each function subscribed to an message.

        :param message: Name of the message.
        :type message: str

        :return: Names of functions subscribed to a specific message.
        :rtype: list
        """
        return [func.__name__ for func in self._messages[message]]

    def _subscribed_message_count(self):
        """ Returns the total amount of subscribed messages.

        :return: Integer amount messages.
        :rtype: int
        """
        message_counter = Counter()

        for key, values in self._messages.items():
            message_counter[key] = len(values)

        return sum(message_counter.values())
