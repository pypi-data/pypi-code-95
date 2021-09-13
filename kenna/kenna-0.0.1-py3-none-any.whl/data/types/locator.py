from dataclasses import dataclass

APPLICATION = 'application'
DATABASE = 'database'
FILE = 'file'
FQDN = 'fqdn'
HOSTNAME = 'hostname'
IP_ADDRESS = 'ip_addr'
MAC_ADDRESS = 'mac_address'
NETBIOS = 'netbios'
URL = 'url'

LOCATOR_TYPES = [
    APPLICATION,
    DATABASE,
    FILE,
    FQDN,
    HOSTNAME,
    IP_ADDRESS,
    MAC_ADDRESS,
    NETBIOS,
    URL,
]


@dataclass(frozen=True)
class Locator:
    id: str
    type: str
    value: str

    def __post_init__(self):
        if self.type not in LOCATOR_TYPES:
            raise ValueError("Invalid locator type: {} (allowed: {})".format(
                self.type, ', '.join(sorted(LOCATOR_TYPES))
            ))
