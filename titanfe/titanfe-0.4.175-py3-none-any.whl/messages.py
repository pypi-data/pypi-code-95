#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""Messages within titanfe"""

from collections import namedtuple
from functools import partial
from enum import IntEnum


class MessageType(IntEnum):
    """Types of Messages used within titanfe"""

    Packet = 20
    PacketRequest = 21
    ConsumerRegistration = 22


Message = namedtuple("Message", ("type", "content"))

# pylint: disable=invalid-name
PacketMessage = partial(Message, MessageType.Packet)
PacketRequest = partial(Message, MessageType.PacketRequest)
ConsumerRegistration = partial(Message, MessageType.ConsumerRegistration)


BrickDescription = namedtuple(
    "BrickDescription",
    (
        "flowuid",
        "flowname",
        "name",
        "brick_type",
        "brick_family",
        "parameters",
        "uid",
        "path_to_module",
        "is_inlet",
        "exit_after_idle_seconds",
        "default_port",
    ),
)
OutputTarget = namedtuple("OutputTarget", ("name", "port", "autoscale_queue_level"))
InputSource = namedtuple("InputSource", ("name", "port", "address"))
