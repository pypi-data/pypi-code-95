import dataclasses

from whoi_nlu_server_messages.CBorMessage import CBorMessage


@dataclasses.dataclass
class Vector3Message(CBorMessage):
    x: float
    y: float
    z: float
