# -*- coding: utf-8 -*-
"""
    pip_services3_commons.commands.__init__
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Commands initialization.

    Contains implementation of Command design patterns,
    which can be used to implement various remote procedure calls (RPCs).
    RPCs replace unique calls with universal "message transfer" calls,
    in which the message itself contains the called method's signature, as well as the parameters to pass for execution.

    When designing calls of methods/commands using the Command
    design pattern, uniform interfaces can be used, which, in turn,
    allow any amount of concrete methods to be called.

    Command design patterns can be used for intercepting messages
    and for various logging implementations.

    These design patterns allow us to create
    :class:`ICommandable <pip_services3_commons.commands.ICommandable.ICommandable>`, which are completely universal.
    If an object extends :class:`ICommandable <pip_services3_commons.commands.ICommandable.ICommandable>` and returns a
    :class:`CommandSet <pip_services3_commons.commands.CommandSet.CommandSet>`, then we can implement, with minimal code, a
    commandable client for this object, using various technologies.

    - :class:`ICommandable <pip_services3_commons.commands.ICommandable.ICommandable>` Commandable – part of the command_name
    design pattern, used to make classes with certain logic, which
    are capable of receiving and processing commands in this
    universal form.

    - :class:`ICommandInterceptor <pip_services3_commons.commands.ICommandInterceptor.ICommandInterceptor>` Command interceptors – modify the
    message execution pipeline. Command interceptors are used to
     intercept calls, perform a set of actions, and, optionally,
    cancel the command_name's actual execution by simply returning a
    result. This logic is used in  aspect-oriented programming.
    Aspect-oriented programming contains perpendicular logic
    (aspects, for example: logging, caching, blocking), which
    can be removed from the business logic and added to these
    perpendicular calls. When using interceptors, a command_name can
    pass through an execution chain, consisting of interceptors,
    which can:
        - simply make some note of the command_name, notify, log,
        get metrics, or do some obj passive task; or
        - intercept the command_name completely and, for example,
        return a previous record of the call from the cache.
    A command_name’s return args can also be intercepted in a similar
    manner: the result can be written to cache, so that the next
    call doesn’t have to be made.

    - :class:`InterceptedCommand <pip_services3_commons.commands.InterceptedCommand.InterceptedCommand>` Intercepted commands are used as
    pattern decorators in the command_name design pattern. They are
    represented as regular commands, but run their own logic
    before calling the actual command_name.

    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

__all__ = [
    'ICommand', 'ICommandInterceptor', 'Command',
    'InterceptedCommand', 'IEvent', 'IEventListener',
    'Event', 'CommandSet', 'ICommandable'
]

from .ICommand import ICommand
from .ICommandInterceptor import ICommandInterceptor
from .Command import Command
from .InterceptedCommand import InterceptedCommand
from .IEvent import IEvent
from .IEventListener import IEventListener
from .Event import Event
from .CommandSet import CommandSet
from .ICommandable import ICommandable
