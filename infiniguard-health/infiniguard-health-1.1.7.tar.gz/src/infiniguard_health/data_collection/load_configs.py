from dataclasses import dataclass
from typing import Callable, Type

from infiniguard_health.blueprints.component_blueprints import (
    TEMPS_BLUEPRINT, FC_BLUEPRINT, DIMMS_BLUEPRINT,
    ETH_BLUEPRINT, PSUS_BLUEPRINT, FANS_BLUEPRINT, VOLUMES_BLUEPRINT, SERVICES_BLUEPRINT, IDRACS_BLUEPRINT,
    DDES_BLUEPRINT, BONDS_BLUEPRINT, SNAPSHOTS_BLUEPRINT, POLICIES_BLUEPRINT
)
from infiniguard_health.blueprints.components import (
    Component, DIMM, EthPort, PSU, Fan, FcPort, TempProbe, Service,
    Volume, BMC, RaidController, IboxConnectivity, Role, RemoteIDRAC, RemoteDDE, Bond, SnapshotsCapacity,
    DDECapacity, Snapshot, Policy, SnapshotSuspendDelete,
)
from infiniguard_health.data_collection.pre_load_parsers import (
    pre_load_parser_omr_psus, pre_load_parser_volumes,
    pre_load_parser_lshw_eth, pre_load_parser_lshw_psu, pre_load_parser_lshw_dimms, pre_load_parser_omr_fans,
    pre_load_parser_snapshots,
)


@dataclass
class LoadConfig:
    config_id: str
    fields_to_load: list
    component_type: Type[Component]
    component_name: str
    component_blueprint: list = None  # None for an IndependentComponent config.
    id_field: str = None  # None if the collector already returns an identified data.
    pre_load_parser_function: Callable = None  # None if pre-loading processing is not required.
    clear_data_when_missing: bool = True  # If True, a missing component will appear without the previous data


omr_memory_load_config = LoadConfig(config_id='omr_memory_load_config',
                                    component_blueprint=DIMMS_BLUEPRINT,
                                    fields_to_load=['status'],
                                    component_type=DIMM,
                                    component_name='dimms',
                                    id_field='connector_name')

omr_psus_load_config = LoadConfig(config_id='omr_psus_load_config',
                                  component_blueprint=PSUS_BLUEPRINT,
                                  fields_to_load=['status', 'online_status', 'firmware_version'],
                                  component_type=PSU,
                                  component_name='psus',
                                  id_field='location_id',
                                  pre_load_parser_function=pre_load_parser_omr_psus)

omr_fans_load_config = LoadConfig(config_id='omr_fans_load_config',
                                  component_blueprint=FANS_BLUEPRINT,
                                  fields_to_load=['rpm', 'name', 'status'],
                                  component_type=Fan,
                                  component_name='fans',
                                  id_field='fan_id',
                                  pre_load_parser_function=pre_load_parser_omr_fans)

ethtool_load_config = LoadConfig(config_id='ethtool_load_config',
                                 component_blueprint=ETH_BLUEPRINT,
                                 fields_to_load=['hardware_revision', 'vendor_pn', 'vendor_sn', 'link_state'],
                                 component_type=EthPort,
                                 component_name='ethernet_ports')

dimms_lshw_load_config = LoadConfig(config_id='dimms_lshw_load_config',
                                    component_blueprint=DIMMS_BLUEPRINT,
                                    id_field='slot',
                                    fields_to_load=['slot', 'asset_tag', 'vendor', 'part_number', 'serial_number',
                                                    'size', 'speed', 'type'],
                                    component_type=DIMM,
                                    pre_load_parser_function=pre_load_parser_lshw_dimms,
                                    component_name='dimms')

eth_lshw_load_config = LoadConfig(config_id='eth_lshw_load_config',
                                  component_blueprint=ETH_BLUEPRINT,
                                  id_field='logicalname',
                                  fields_to_load=['vendor', 'model', 'serial_number', 'firmware_version', 'driver',
                                                  'driver_version', 'type', 'port_name', 'auto_negotiation', 'duplex'],
                                  component_type=EthPort,
                                  pre_load_parser_function=pre_load_parser_lshw_eth,
                                  component_name='ethernet_ports')

psu_lshw_load_config = LoadConfig(config_id='psu_lshw_load_config',
                                  component_blueprint=PSUS_BLUEPRINT,
                                  id_field='physid',
                                  fields_to_load=['product_id', 'vendor', 'serial_number', 'capacity'],
                                  component_type=PSU,
                                  pre_load_parser_function=pre_load_parser_lshw_psu,
                                  component_name='psus')

fcports_gc_load_config = LoadConfig(config_id='fcports_gc_load_config',
                                    component_blueprint=FC_BLUEPRINT,
                                    id_field='pcibus',
                                    fields_to_load=['role', 'alias', 'slot'],
                                    component_type=FcPort,
                                    component_name='fc_ports')

fcports_driver_version_load_config = LoadConfig(config_id='fcports_driver_version_load_config',
                                                component_blueprint=FC_BLUEPRINT,
                                                id_field='pcibus',
                                                fields_to_load=['firmware_version'],
                                                component_type=FcPort,
                                                component_name='fc_ports')

fcports_lspci_load_config = LoadConfig(config_id='fcports_lspci_load_config',
                                       component_blueprint=FC_BLUEPRINT,
                                       id_field='pcibus',
                                       fields_to_load=['vendor', 'model', 'serial_number',
                                                       'hba_info', 'hardware_revision'],
                                       component_type=FcPort,
                                       component_name='fc_ports')

fcports_sysfs_load_config = LoadConfig(config_id='fcports_sysfs_load_config',
                                       component_blueprint=FC_BLUEPRINT,
                                       id_field='pcibus',
                                       fields_to_load=['wwn', 'wwpn', 'connection_speed',
                                                       'maximum_speed', 'enabled', 'link_state'],
                                       component_type=FcPort,
                                       component_name='fc_ports')

fcports_sfp_info_load_config = LoadConfig(config_id='fcports_sfp_info_load_config',
                                          component_blueprint=FC_BLUEPRINT,
                                          id_field='pcibus',
                                          fields_to_load=['sfp_vendor_name', 'sfp_vendor_pn', 'sfp_vendor_revision',
                                                          'sfp_vendor_sn', 'sfp_supported_speeds'],
                                          component_type=FcPort,
                                          component_name='fc_ports')

temps_load_config = LoadConfig(config_id='temps_load_config',
                               component_blueprint=TEMPS_BLUEPRINT,
                               id_field='probe_name',
                               fields_to_load=['probe_name', 'temp', 'status'],
                               component_type=TempProbe,
                               component_name='temperatures')

syscli_eth_load_config = LoadConfig(config_id='syscli_eth_load_config',
                                    component_blueprint=ETH_BLUEPRINT,
                                    fields_to_load=['maximum_speed', 'mtu', 'enabled', 'interfaces_count',
                                                    'interfaces'],
                                    component_type=EthPort,
                                    component_name='ethernet_ports')

services_load_config = LoadConfig(config_id='services_load_config',
                                  component_blueprint=SERVICES_BLUEPRINT,
                                  fields_to_load=['name', 'status'],
                                  component_type=Service,
                                  component_name='services')

volumes_load_config = LoadConfig(config_id='volumes_load_config',
                                 component_blueprint=VOLUMES_BLUEPRINT,
                                 fields_to_load=['device_name', 'volume_name', 'wwid', 'number_of_active_paths'],
                                 component_type=Volume,
                                 component_name='volumes',
                                 id_field='volume_id',
                                 pre_load_parser_function=pre_load_parser_volumes)

omr_bmc_load_config = LoadConfig(config_id='omr_bmc_load_config',
                                 fields_to_load=['ipmi_ip', 'ipmi_gw_ip', 'ipmi_ip_source', 'ipmi_subnet',
                                                 'ipmi_mac', 'sol_enabled', 'ipmi_over_lan_enabled'],
                                 component_type=BMC,
                                 component_name='bmc')

omr_raidcontroller_load_config = LoadConfig(config_id='omr_raidcontroller_load_config',
                                            fields_to_load=['model', 'firmware_version', 'driver_version', 'status'],
                                            component_type=RaidController,
                                            component_name='raid_controller')

ibox_connectivity_load_config = LoadConfig(config_id='ibox_connectivity_load_config',
                                           fields_to_load=['is_connected'],
                                           component_type=IboxConnectivity,
                                           component_name='ibox_connectivity')

role_load_config = LoadConfig(config_id='role_load_config',
                              fields_to_load=['management_ip', 'role_id'],
                              component_type=Role,
                              component_name='role')

remote_ddes_load_config = LoadConfig(config_id='remote_ddes_load_config',
                                     component_blueprint=DDES_BLUEPRINT,
                                     fields_to_load=['role', 'has_ssh_connection', 'ssh_conn_error_msg'],
                                     component_type=RemoteDDE,
                                     component_name='remote_ddes',
                                     id_field='role')

remote_idracs_load_config = LoadConfig(config_id='remote_idracs_load_config',
                                       component_blueprint=IDRACS_BLUEPRINT,
                                       fields_to_load=['idrac_id', 'has_redfish_connection',
                                                       'redfish_connect_error_msg'],
                                       component_type=RemoteIDRAC,
                                       component_name='remote_idracs',
                                       id_field='idrac_id')

bonds_load_config = LoadConfig(config_id='bonds_load_config',
                               component_blueprint=BONDS_BLUEPRINT,
                               fields_to_load=['driver_version', 'bonding_mode', 'status',
                                               'mii_polling_interval_ms', 'slaves'],
                               component_type=Bond,
                               component_name='bonds')

snapshots_capacity_load_config = LoadConfig(config_id='snapshots_capacity_load_config',
                                            fields_to_load=['used_snapshot_capacity_percent'],
                                            component_type=SnapshotsCapacity,
                                            component_name='snapshots_capacity')

dde_capacity_load_config = LoadConfig(config_id='dde_capacity_load_config',
                                      fields_to_load=['used_dde_capacity_percent'],
                                      component_type=DDECapacity,
                                      component_name='dde_capacity')

snapshots_load_config = LoadConfig(config_id='snapshots_load_config',
                                   component_blueprint=SNAPSHOTS_BLUEPRINT,
                                   fields_to_load=['originated_by', 'snapshot_id', 'created_at', 'expires_at',
                                                   'lock_expires_at', 'ddeapp', 'label', 'lock_state',
                                                   'original_policy'],
                                   component_type=Snapshot,
                                   component_name='snapshots',
                                   id_field='snapid',
                                   pre_load_parser_function=pre_load_parser_snapshots,
                                   clear_data_when_missing=False)

polices_load_config = LoadConfig(config_id='policies_load_config',
                                 component_blueprint=POLICIES_BLUEPRINT,
                                 fields_to_load=['policy_type', 'enabled', 'frequency', 'immutable', 'retention'],
                                 component_type=Policy,
                                 component_name='policies',
                                 id_field='policy_type')

snapshot_suspend_delete_load_config = LoadConfig(config_id='snapshot_suspend_delete_load_config',
                                                 fields_to_load=['suspend_delete'],
                                                 component_type=SnapshotSuspendDelete,
                                                 component_name='snapshot_suspend_delete')
