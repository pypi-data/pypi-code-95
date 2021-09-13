from typing import Optional

import dataclasses

from whoi_nlu_server_messages.CBorMessage import CBorMessage


@dataclasses.dataclass
class NetworkDescriptionMessage(CBorMessage):
    control_hostname: str = ""
    control_port: int = 0
    data_hostname: str = ""
    data_port: int = 0
    speech_to_text_hostname: str = ""
    speech_to_text_port: int = 0
    h2sl_hostname: str = ""
    h2sl_port: int = 0
