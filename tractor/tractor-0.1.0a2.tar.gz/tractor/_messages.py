'''
Typed messaging with ``msgspec``.

'''
from typing import Any

import msgspec


# Define a schema for a `User` type
class Msg(msgspec.Struct):
    cid: str
    cmd: dict[str, Any]

# Serialize `alice` to `bytes` using the MessagePack protocol
serialized_data = msgspec.encode(alice)
