import logging
import os
from glob import glob
from typing import List

import infinisdk
from iba_install.lib.ddenode import iter_dde_nodes
from infi.caching import cached_function
from infi.storagemodel.vendor.infinidat.shortcuts import get_infinidat_native_multipath_block_devices

from infiniguard_health.data_collection.parsers import( lshw_parser, omreport_parser, ethtool_parser, syscli_parser,
    syscli_map_interfaces_to_devices, omr_system_versions_parser, volumes_parser, lspci_fc_parser, gc_fcports_parser,
    bond_parser)
from infiniguard_health.data_collection.sources import (lshw_source, omreport_chassis_info, omreport, syscli, ethtool,
    gc_fcports, fc_driver_version, lspci_fc, sysfs_fc_info, sfp_details, service_status, has_ibox_connectivity,
    get_dde_role, get_mgmt_ip, host_to_alias_mapping, check_redfish_idrac_connection
)
from infiniguard_health.utils import (
    HostCommandException, host_to_pcibus_mapping, max_speed,
    multiple_indexes_from_iter,
    formatter, get_local_dde_node,
    get_local_dde_app_id,
)

_logger = logging.getLogger(__name__)


def lshw_data():
    return lshw_parser(lshw_source())


def omr_memory():
    return omreport_parser(omreport_chassis_info('memory'))


def omr_power_supplies():
    return omreport_parser(omreport_chassis_info('pwrsupplies'))


def omr_fans():
    fans_data = omreport_parser(omreport_chassis_info('fans'))
    for fan in fans_data:
        fan['rpm'] = int(fan.get('reading').replace('RPM', ''))
    return fans_data


def omr_bmc():
    return omreport_parser(omreport_chassis_info('remoteaccess'))


def omr_raid_controller():
    return omreport_parser(omreport('storage', 'controller'))[0]


def omr_temps():
    return omreport_parser(omreport_chassis_info('temps'))


def syscli_eth_data():
    data = syscli_parser(syscli('--list', 'interface'))
    return syscli_map_interfaces_to_devices(data)


def ethtool_data():
    from infiniguard_health.blueprints.component_blueprints import ETH_BLUEPRINT
    ethtool_args = ('', '-m')

    def ethtool_combine_data_of_args(port):
        data = {}
        for arg in ethtool_args:
            try:
                data.update(ethtool_parser(ethtool(port, arg)))
            except HostCommandException as e:
                data.update({'Error': e.args[2]})
        return data

    return {port: ethtool_combine_data_of_args(port) for port in ETH_BLUEPRINT}


def omr_system_versions():
    return omr_system_versions_parser(omreport('system', 'version'))


def fc_ports_gc():
    formatting_directives = [
        (('owner', 'role', False), lambda s: 'frontend' if s == 'user' else 'backend'),
    ]

    return {alias: formatter(port_data, formatting_directives)
            for alias, port_data
            in gc_fcports_parser(gc_fcports(xml=True)).items()}


def fc_ports_driver_version():
    return {host_to_alias_mapping().get(host): {'firmware_version': fc_driver_version(pcibus)}
            for host, pcibus in host_to_pcibus_mapping().items()}


def fc_ports_lspci():
    formatting_directives = [
        (('hba_info', 'vendor', True), lambda s: ' '.join(multiple_indexes_from_iter((0, 1), s.split()))),
    ]
    return {host_to_alias_mapping().get(host): formatter(lspci_fc_parser(lspci_fc(pcibus)), formatting_directives)
            for host, pcibus in host_to_pcibus_mapping().items()}


def fc_ports_sysfs():
    formatting_directives = [
        ('port_name', lambda s: s.replace('0x', '')),
        ('node_name', lambda s: s.replace('0x', '')),
        (('supported_speeds', 'maximum_speed', False), max_speed),
        ('port_state', lambda s: 'Yes' if s == 'Online' else 'No'),
        ('link_state', lambda s: 'Up' if 'Up' in s else 'Down'),
    ]
    return {host_to_alias_mapping().get(host): formatter(sysfs_fc_info(host), formatting_directives)
            for host in host_to_pcibus_mapping().keys()}


def fc_ports_sfp_info():
    return {host_to_alias_mapping().get(host): sfp_details(host) for host in host_to_pcibus_mapping().keys()}


def services_info():
    from infiniguard_health.blueprints.component_blueprints import SERVICES_BLUEPRINT
    return {service: {'name': service, 'status': service_status(service)}
            for service
            in SERVICES_BLUEPRINT}


# Due to a bug in gevent (?) - using get_infinidat_native_multipath_block_devices creates dangling epoll file
# descriptors which eventually cause the process to go over the limit of allowed open files, and crash.
# As a workaround (after exhausting all other possibilities) - this data will have to be cached, and stale...
@cached_function
def volumes_data():
    return volumes_parser(get_infinidat_native_multipath_block_devices())


def ibox_connectivity_info():
    return {'is_connected': has_ibox_connectivity()}


def role_info():
    return {
        'management_ip': get_mgmt_ip(),
        'role_id': get_dde_role()
    }


def check_ssh_connection_to_ddes():
    for node in iter_dde_nodes():
        has_ssh_connection, dde_ssh_conn_error_msg = node.check_ssh_connection()
        yield {
            'role': node.role,
            'has_ssh_connection': has_ssh_connection,
            'ssh_conn_error_msg': dde_ssh_conn_error_msg
        }


def check_redfish_connection_to_idracs():
    for node in iter_dde_nodes():
        has_redfish_connection, redfish_connection_error_msg = check_redfish_idrac_connection(node)

        yield {
            'idrac_id': node.nodeid,
            'has_redfish_connection': has_redfish_connection,
            'redfish_connect_error_msg': redfish_connection_error_msg
        }


def proc_net_bonding_data():
    def _read_bond_file(path):
        with open(path) as f:
            return f.read()

    return {os.path.basename(bond): bond_parser(_read_bond_file(bond)) for bond in glob('/proc/net/bonding/bond*')}


def snapshots_capacity_data():
    from iba_api.snapshot.capacity_reporter import CapacityReporter

    # Percent is represented as a float between 0 and 1
    return {'used_snapshot_capacity_percent': CapacityReporter().get_capacity_used_percent()}


def dde_capacity_data():
    from iba_mgmt.lib.dde_api import SysCli
    disk_usage = SysCli().get_disk_usage().to_dict

    # Percent is represented as a float between 0 and 1
    if disk_usage['disk_capacity'] == 0:
        used_percent = 0.0
    else:
        used_percent = round(disk_usage['used_disk_space'] / disk_usage['disk_capacity'], 6)
    return {'used_dde_capacity_percent': used_percent}


def snapshots_data() -> List[dict]:
    from iba_api.snapshot.list_snapshots import list_snap
    snapshots = []

    for ddesnap in list_snap(get_local_dde_app_id(), omit_sizes=True):
        try:
            snapshot_schema_as_dict = ddesnap.snapschema.to_dict()
        except infinisdk.core.exceptions.APICommandFailed as e:
            if e.error_code == 'CG_NOT_FOUND':
                _logger.debug(f"Snapshot {ddesnap.sg} has been deleted during iteration. Skipping its collection")
                continue
            raise

        lock_expires_at = ddesnap.sg.get_lock_expires_at(from_cache=True)  # Returns arrow object
        snapshot_schema_as_dict['lock_expires_at'] = int(
            lock_expires_at.float_timestamp * 1000) if lock_expires_at else None
        # updated_at field of snapshot interferes with updated_at field of infiniguard-health Component
        del snapshot_schema_as_dict['updated_at']
        snapshots.append(snapshot_schema_as_dict)

    return snapshots


def policies_data() -> List[dict]:
    from iba_api.snapshot.ddepolicy import DdePolicyManager
    from iba_api.server.models import OriginatedByType

    system_policy = DdePolicyManager(get_local_dde_app_id(), OriginatedByType.SYSTEM_POLICY).get_policy().to_dict()
    system_policy['policy_type'] = OriginatedByType.SYSTEM_POLICY

    user_policy = DdePolicyManager(get_local_dde_app_id(), OriginatedByType.USER_POLICY).get_policy().to_dict()
    user_policy['policy_type'] = OriginatedByType.USER_POLICY

    return [system_policy, user_policy]


def snapshot_suspend_delete_data():
    from iba_api.snapshot.ddepolicy import DdeSuspendDeletePolicyManager

    return DdeSuspendDeletePolicyManager(get_local_dde_app_id()).get_policy().to_dict()
