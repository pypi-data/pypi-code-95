"""
Sources are the building blocks of the data collection.
They are the lowest level of data retreival functions,
which suppose to have minimal to none data parsing or formatting.
"""

import json
import re
import struct
from glob import glob
from typing import Tuple

from iba_install.core.ibox import get_ibox
from iba_install.lib.ddenode import DdeNode
from infinisdk.core.exceptions import APITransportFailure, APICommandFailed

from infiniguard_health.utils import (
    host_command, sfp_supported_speeds, HostCommandException, get_ip_addresses,
    MgmtIPsException, get_local_dde_role
)


def lshw_source():
    command = 'lshw -json'
    return json.loads(host_command(command))


def omreport(component, subcomponent):
    command = '/opt/dell/srvadmin/bin/omreport {} {} -fmt ssv'.format(component, subcomponent)
    return host_command(command)


def omreport_chassis_info(subcomponent):
    return omreport(component='chassis', subcomponent=subcomponent)


def ethtool(interface, flag=''):
    command = f'ethtool {flag} {interface}'
    return host_command(command)


def systemctl():
    command = 'systemctl --no-pager --no-legend'
    return host_command(command)


def sfp_details(host):
    vendor_name, supported_speeds, vendor_pn, vendor_revision, vendor_sn = [None] * 5
    sfp_path = f'/sys/class/fc_host/{host}/device/sfp'
    try:
        with open(sfp_path, 'rb') as f:
            supported_speeds, \
            vendor_name, \
            vendor_pn, \
            vendor_revision, \
            vendor_sn = [detail.decode().rstrip() if isinstance(detail, bytes) else detail
                         for detail
                         in struct.unpack('10xB9x16s4x16s4s8x16s428x', f.read())]
            supported_speeds = sfp_supported_speeds(supported_speeds)

    except Exception:
        pass
    return {
        'sfp_vendor_name': vendor_name,
        'sfp_vendor_pn': vendor_pn,
        'sfp_vendor_revision': vendor_revision,
        'sfp_vendor_sn': vendor_sn,
        'sfp_supported_speeds': supported_speeds
    }


def sysfs_fc_info(host):
    data_files = ('port_name', 'node_name', 'port_state', 'speed',
                  'supported_speeds', f'device/scsi_host/{host}/link_state')

    return {file.split('/')[-1]: host_command(f'cat /sys/class/fc_host/{host}/{file}').strip() for file in data_files}


def fc_driver_version(pcibus):
    driver_version_path = glob(f'/sys/bus/pci/drivers/qla*/{pcibus}/driver/module/version')[0]
    return host_command(f'cat {driver_version_path}').strip()


def lspci_fc(pcibus):
    return host_command(f'lspci -kvv -s {pcibus}')


def syscli(*args):
    return host_command(f'/opt/DXi/syscli {" ".join(args)}')


def gc_fcports(xml=False):
    command = '/opt/DXi/gc --list fcports'
    if xml:
        command = f'{command} --xml'
    return host_command(command)


def host_to_alias_mapping():
    mapping = {}
    for line in gc_fcports().splitlines()[2:]:
        host_match = re.search('host\d+', line)
        alias_match = re.search('fc\dp\d', line)
        if host_match and alias_match:
            mapping[host_match.group()] = alias_match.group()
    return mapping


def service_status(service_name):
    try:
        return host_command(f'systemctl is-active {service_name}').replace('\n', '')
    except HostCommandException as e:
        info_arg = 1
        return e.args[info_arg].replace('\n', '')


def has_ibox_connectivity():
    ibox = get_ibox()
    try:
        with ibox.api.change_request_default_timeout_context(2):
            is_active = ibox.is_active()
    except (APITransportFailure, APICommandFailed):
        return False
    return is_active


def get_mgmt_ip():
    try:
        [mgmt_ip] = [ip for ip in get_ip_addresses() if ip.startswith('9.151.140.12')]
    except ValueError:  # unpack error
        raise MgmtIPsException('There are more than one or none mgmt ips!')
    return mgmt_ip


def get_dde_role():
    return get_local_dde_role()


def check_redfish_idrac_connection(node: DdeNode) -> Tuple[bool, str]:
    """
    Checks if the idrac of the given node can be reached via redfish (an HTTP connection).
    Returns a tuple: (result_of_check, error_message)
    """
    from iba_api.idrac_connection import NodeIdracRedfishConnection

    try:
        with NodeIdracRedfishConnection(node) as idrac:
            idrac.powerstatus()
        return True, ''

    except Exception as e:
        return False, str(e)
