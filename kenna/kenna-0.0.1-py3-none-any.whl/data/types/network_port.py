from dataclasses import dataclass
from typing import Optional

from kenna.data.constants.network_port_state import OPEN
from kenna.data.constants.network_protocol_type import TCP, UDP


@dataclass(frozen=True)
class NetworkPort:
    id: int
    name: str
    port_number: int
    protocol: str
    state: str

    #: Optional fields.
    product: Optional[str]
    version: Optional[str]
    os_type: Optional[str]
    hostname: Optional[str]
    extra_info: Optional[str]

    def is_unknown_protocol(self):
        return self.name == "<unknown>" or not self.name

    def is_open(self):
        return self.state == OPEN

    def is_tcp_port(self):
        return self.protocol == TCP

    def is_udp_port(self):
        return self.protocol == UDP
