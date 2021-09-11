import dataclasses
from typing import List

from whoi_nlu_server_messages.CBorMessage import CBorMessage


@dataclasses.dataclass
class StringListMessage(CBorMessage):
    data: List[str]
