#  Copyright (c)  2021  Allthenticate
"""
This module contains utility functions for interacting over dbus using dbus-next

For references of this implementation see:

DBUS: https://dbus.freedesktop.org/doc/dbus-specification.html
dbus-next: https://python-dbus-next.readthedocs.io/_/downloads/en/latest/pdf/
"""

# Dependencies
import re

# 3rd party
from typing import Optional

from dbus_next import Message
from dbus_next.aio import MessageBus
from dbus_next.constants import MessageType


async def add_match(bus: MessageBus, match_rule: str = "type='signal'") -> None:
    """
    Calls the function `AddMatch` to add a match rule so when signals that match the match rule are emitted,
    the bus' handler will receive them.

    :param bus: the bus which will serve as the handler
    :type bus: MessageBus
    :param match_rule: the match rule to filter all messages going over the bus (default is type='signal')
    :type match_rule: str
    :return: None
    :rtype: None
    """
    reply: Optional[Message] = await bus.call(
        Message(
            destination="org.freedesktop.DBus",
            path="/org/freedesktop/DBus",
            interface="org.freedesktop.DBus",
            member="AddMatch",
            signature="s",
            body=[match_rule],
        )
    )

    # Validate the response
    if reply is None:
        raise RuntimeWarning("No message back from adding match rule")

    assert reply.message_type == MessageType.METHOD_RETURN, reply.error_name


async def remove_match(bus: MessageBus, match_rule: str = "type='signal'") -> None:
    """
    Calls the function `RemoveMatch` to remove a match rule so when signals that match the match rule are emitted,
    the bus' handler will NO longer receive them.

    :param bus: the bus which was the handler
    :type bus: MessageBus
    :param match_rule: the match rule to filter all messages going over the bus (default is type='signal')
    :type match_rule: str
    :return: None
    :rtype: None
    """
    reply: Optional[Message] = await bus.call(
        Message(
            destination="org.freedesktop.DBus",
            path="/org/freedesktop/DBus",
            interface="org.freedesktop.DBus",
            member="RemoveMatch",
            signature="s",
            body=[match_rule],
        )
    )

    # Validate the response
    if reply is None:
        raise RuntimeWarning("No message back from removing match rule")

    assert reply.message_type == MessageType.METHOD_RETURN, reply.error_name


def parse_identifier_from_path(dbus_path: str) -> str:
    """
    Parses the identifier (eg. mac address) of a device from the dbus path

    ex. /org/bluez/hci0/dev_6B_0A_12_1A_7D_60

    :param dbus_path: the dbus path of the device
    :type dbus_path: str
    :return: the parsed out identifier
    :rtype: str
    """
    regex = re.compile(r"(?:[0-9a-fA-F]_?){12}")
    match = re.findall(regex, dbus_path)

    if not match:
        ValueError("Inputted a dbus path that did not contain a mac address")

    # Return the entry with underscores swapped
    return match[0].replace("_", ":")
