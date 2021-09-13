from hodgepodge.platforms import WINDOWS
from kenna.data.types.asset_group import AssetGroup
from kenna.data.types.asset import Asset
from kenna.data.types.network_port import NetworkPort

import hodgepodge
import hodgepodge.time
import logging

logger = logging.getLogger(__name__)


def parse_asset(data: dict) -> Asset:
    return Asset(
        application=data['application'],
        asset_groups=[parse_asset_group(g) for g in data['asset_groups']],
        container=data['container'],
        create_time=hodgepodge.time.as_epoch_timestamp(data['created_at']),
        database=data['database'],
        ec2=data['ec2'],
        external_id=data['external_id'],
        file=data['file'],
        fqdn=data['fqdn'],
        hostname=data['hostname'],
        id=data['id'],
        image=data['image'],
        inactive_time=hodgepodge.time.as_epoch_timestamp(data['inactive_at']),
        primary_ipv4_address=data['ip_address'],
        primary_ipv6_address=data['ipv6'],
        primary_mac_address=data['mac_address'],
        last_boot_time=hodgepodge.time.as_epoch_timestamp(data['last_booted_at']),
        last_seen_time=hodgepodge.time.as_epoch_timestamp(data['last_seen_time']),
        locator=data['locator'],
        network_ports=[parse_network_port(p) for p in data['network_ports']],
        number_of_vulnerabilities=data['vulnerability_count'],
        os_version=data['operating_system'],
        owner=data['owner'],
        primary_locator=data['primary_locator'],
        priority=data['priority'],
        risk_meter_score=data['risk_meter_score'],
        status=data['status'],
        status_set_manually=data['status_set_manually'],
        tags=data['tags'],
        urls=data['urls'],
        netbios=data['netbios'],
        notes=data['notes'],
    )


def parse_network_port(data: dict) -> NetworkPort:
    name = data['name'] or None
    if name and name == '<unknown>':
        name = None

    return NetworkPort(
        id=data['id'],
        name=name,
        state=data['state'],
        port_number=data['port_number'],
        protocol=data['protocol'],
        extra_info=data['extra_info'] or None,
        hostname=data['hostname'] or None,
        os_type=data['ostype'] or None,
        product=data['product'] or None,
        version=data['version'] or None,
    )


def parse_asset_group(data: dict) -> AssetGroup:
    return AssetGroup(id=data['id'], name=data['name'])
