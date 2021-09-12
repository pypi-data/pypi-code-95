# -*- coding: utf-8 -*-
"""
    pip_services3_commons.run.Notifier
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Notifier component implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Any, List, Optional

from .INotifiable import INotifiable
from .Parameters import Parameters


class Notifier:
    """
    Helper class that notifies components.
    """

    @staticmethod
    def notify_one(correlation_id: Optional[str], component: Any, args: Parameters):
        """
        Notifies specific component.
        To be notiied components must implement :class:`INotifiable <pip_services3_commons.run.INotifiable.INotifiable>` interface.
        If they don't the call to this method has no effect.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param component: the component that is to be notified.

        :param args: notifiation arguments.
        """
        if component is None:
            return

        if isinstance(component, INotifiable):
            component.notify(correlation_id, args)

    @staticmethod
    def notify(correlation_id: Optional[str], components: List[Any], args: Parameters = None):
        """
        Notifies multiple components.

        To be notified components must implement :class:`INotifiable <pip_services3_commons.run.INotifiable.INotifiable>` interface.
        If they don't the call to this method has no effect.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param components: a list of components that are to be notified.

        :param args: notification arguments.
        """
        if components is None:
            return

        args = args if not (args is None) else Parameters()
        for component in components:
            Notifier.notify_one(correlation_id, component, args)
