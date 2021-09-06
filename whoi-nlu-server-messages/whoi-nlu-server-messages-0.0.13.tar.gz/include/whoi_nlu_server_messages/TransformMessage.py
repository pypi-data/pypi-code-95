import dataclasses
from cbor2 import loads

from whoi_nlu_server_messages.CBorMessage import CBorMessage
from whoi_nlu_server_messages.QuaternionMessage import QuaternionMessage
from whoi_nlu_server_messages.Vector3Message import Vector3Message


@dataclasses.dataclass
class TransformMessage(CBorMessage):
    translation: Vector3Message
    rotation: QuaternionMessage

    def as_dict(self) -> dict:
        return {
            "translation": self.translation.as_dict(),
            "rotation": self.rotation.as_dict(),
        }

    # @classmethod
    # def from_bytes(cls, data: bytes) -> 'TransformMessage':
    #     d = loads(data)
    #     return TransformMessage(
    #         translation=Vector3Message(**d["translation"]),
    #         rotation=QuaternionMessage(**d["rotation"]),
    #     )

