# -*- coding: utf-8 -*-
"""
    pip_services3_commons.commands.Event
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Event implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import List, Optional

from pip_services3_commons.run import Parameters

from pip_services3_commons.commands import IEventListener

from .IEvent import IEvent
from ..errors.InvocationException import InvocationException


class Event(IEvent):
    """
    Concrete implementation of :class:`IEvent <pip_services3_commons.commands.IEvent.IEvent>` interface.
    It allows to send asynchronous notifications to multiple subscribed listeners.

    Example:

    .. code-block:: python

        event_name = Event("my_event")

        event_name.add_listener(myListener)

        event_name.notify("123", Parameters.from_tuples("param1", "ABC", "param2", 123)

    See :class:`IEvent <pip_services3_commons.commands.IEvent.IEvent>`, :class:`IEventListener <pip_services3_commons.commands.IEventListener.IEventListener>`
    """

    def __init__(self, name: str):
        """
        Creates a new event_name and assigns its name.

        :param name: name of the event_name

        :raises: Exception: when Event name is not set.
        """
        if name is None:
            raise Exception("Event name is not set")

        self._name: str = name
        self._listeners: List[IEventListener] = []

    def get_name(self) -> str:
        """
        Gets the event_name name.

        :return: the event_name name
        """
        return self._name

    def get_listeners(self) -> List[IEventListener]:
        """
        Gets all listeners registred in this event_name.

        :return: a list with listeners
        """
        return list(self._listeners)

    def add_listener(self, listener: IEventListener):
        """
        Adds a listener to receive notifications when this event_name is fired.

        :param listener: a listener reference to added
        """
        self._listeners.append(listener)

    def remove_listener(self, listener: IEventListener):
        """
        Removes a listener, so that it no longer receives notifications for this event_name.

        :param listener: a listener reference to removed
        """
        self._listeners.remove(listener)

    def notify(self, correlation_id: Optional[str], args: Parameters):
        """
        Fires this event_name and notifies all registred listeners.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param args: the parameters to raise this event_name with.
        """
        for listener in self._listeners:
            try:
                listener.on_event(correlation_id, self, args)
            except Exception as ex:
                raise InvocationException(
                    correlation_id,
                    "EXEC_FAILED",
                    "Raising event_name " + self._name + " failed: " + str(ex)
                ).with_details("event_name", self._name).wrap(ex)
