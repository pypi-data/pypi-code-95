from dataclasses import dataclass
from typing import List, Optional, Dict, Iterable
from kenna.data.types.asset_group import AssetGroup
from kenna.data.types.locator import Locator
from kenna.data.types.network_port import NetworkPort

import hodgepodge.patterns
import hodgepodge.platforms


@dataclass(frozen=True)
class Asset:
    application: str
    external_id: str
    database: str               #: "The database name of the asset."
    ec2: str                    #: "The ec2 name of the asset."
    file: str                   #: "The Fully Qualified path of the file."
    fqdn: str
    hostname: str
    inactive: bool
    ipv4_addresses: List[str]
    ipv6_addresses: List[str]
    mac_addresses: List[str]
    last_boot_time: float
    last_seen_time: float
    netbios: str                #: "The NetBIOS address of the asset."
    notes: List[str]
    os_version: str
    owner: str
    priority: int               #: "The priority of the asset; an integer between 1 (low) to 10 (high)."
    url: str                    #: "The URL of the asset."

    @property
    def ip_addresses(self) -> List[str]:
        return self.ipv4_addresses + self.ipv6_addresses

    @property
    def ip_address(self):
        return next(iter(self.ip_addresses))

    @property
    def ipv4_address(self):
        return next(iter(self.ipv4_addresses), None)

    @property
    def ipv6_address(self):
        return next(iter(self.ipv6_addresses), None)

    @property
    def os_type(self) -> str:
        return hodgepodge.platforms.parse_os_type(self.os_version)

    def has_matching_hostname(self, hostnames: Iterable[str]) -> bool:
        return self.hostname and hodgepodge.patterns.string_matches_any_glob(self.hostname, patterns=hostnames)

    def has_matching_ip_address(self, ip_addresses: Iterable[str]) -> bool:
        ips = self.ip_addresses
        return ips and hodgepodge.patterns.any_string_matches_any_glob(values=ips, patterns=ip_addresses)

    def has_matching_mac_address(self, mac_addresses: Iterable[str]) -> bool:
        return self.mac_address and hodgepodge.patterns.string_matches_any_glob(self.mac_address, mac_addresses)

    def is_aws_ec2_instance(self):
        return bool(self.ec2)

    def is_container(self):
        return bool(self.container)

    def is_inactive(self):
        return self.inactive
