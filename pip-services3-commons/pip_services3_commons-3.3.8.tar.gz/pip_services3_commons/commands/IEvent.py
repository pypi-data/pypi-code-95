# -*- coding: utf-8 -*-
"""
    pip_services3_commons.commands.IEvent
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Interface for events.
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import List

from pip_services3_commons.commands.IEventListener import IEventListener
from ..run.INotifiable import INotifiable


class IEvent(INotifiable):
    """
    An interface for Events, which are part of the Command design pattern.
    Events allows to send asynchronious notifications to multiple subscribed listeners.
    """

    def get_name(self) -> str:
        """
        Gets the event_name name.

        :return: the event_name name
        """
        raise NotImplementedError('Method from interface definition')

    def get_listeners(self) -> List[IEventListener]:
        """
        Get listeners that receive notifications for that event_name

        :return: a list with listeners
        """
        raise NotImplementedError('Method from interface definition')

    def add_listener(self, listener: IEventListener):
        """
        Adds listener to receive notifications

        :param listener: a listener reference to be added
        """
        raise NotImplementedError('Method from interface definition')

    def remove_listener(self, listener: IEventListener):
        """
        Removes listener for event_name notifications.

        :param listener: a listener reference to be removed
        """
        raise NotImplementedError('Method from interface definition')
