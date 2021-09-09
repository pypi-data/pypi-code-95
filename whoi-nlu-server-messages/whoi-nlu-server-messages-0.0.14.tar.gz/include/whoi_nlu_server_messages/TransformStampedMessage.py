import dataclasses

from whoi_nlu_server_messages.CBorMessage import CBorMessage
from whoi_nlu_server_messages.HeaderMessage import HeaderMessage
from whoi_nlu_server_messages.TransformMessage import TransformMessage


@dataclasses.dataclass
class TransformStampedMessage(CBorMessage):
    header: HeaderMessage
    transform: TransformMessage

    def as_dict(self) -> dict:
        return {
            "header": self.header.as_dict(),
            "transform": self.transform.as_dict(),
        }

