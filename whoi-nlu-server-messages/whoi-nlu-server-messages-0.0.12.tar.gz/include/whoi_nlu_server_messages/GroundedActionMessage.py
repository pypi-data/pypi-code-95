import dataclasses

from whoi_nlu_server_messages.CBorMessage import CBorMessage
from whoi_nlu_server_messages.GroundedActionParamMessage import GroundedActionParamMessage


@dataclasses.dataclass
class GroundedActionMessage(CBorMessage):
    name: str
    params: list # List contains GroundedActionParamMessages
