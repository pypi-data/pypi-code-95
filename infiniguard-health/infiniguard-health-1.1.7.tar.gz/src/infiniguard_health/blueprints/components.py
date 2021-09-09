from __future__ import annotations

import bisect
import copy
import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from enum import Enum, auto
from functools import total_ordering

from arrow import Arrow
from munch import munchify
from schematics.transforms import blacklist
from schematics.types import StringType, IntType, IPv4Type, BooleanType, FloatType
from schematics.types.compound import ModelType, ListType

from infiniguard_health.blueprints import (
    DataModel, YesNoType, UpDownType, OnOffType, EnumType, ActiveInactiveType,
    ArrowType
)
from infiniguard_health.utils import get_local_node_id, get_default_policy_types, get_latest_time, get_current_ibox_time

_logger = logging.getLogger(__name__)

SYSTEM_COMPONENT_NAMES = munchify({
    'dimms': 'dimms',
    'psus': 'psus',
    'fans': 'fans',
    'bmc': 'bmc',
    'raid_controller': 'raid_controller',
    'ethernet_ports': 'ethernet_ports',
    'bonds': 'bonds',
    'fc_ports': 'fc_ports',
    'temperatures': 'temperatures',
    'services': 'services',
    'volumes': 'volumes',
    'ibox_connectivity': 'ibox_connectivity',
    'role': 'role',
    'remote_ddes': 'remote_ddes',
    'remote_idracs': 'remote_idracs',
    'snapshots_capacity': 'snapshots_capacity',
    'dde_capacity': 'dde_capacity',
    'snapshots': 'snapshots',
    'policies': 'policies',
    'snapshot_suspend_delete': 'snapshot_suspend_delete'
})


@total_ordering
class ComponentState(Enum):
    NORMAL = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()

    def __lt__(self, other):
        if self.__class__ is not other.__class__:
            return NotImplemented

        return self.value < other.value


class ComponentMergeError(Exception):
    """Raised when trying to perform a forbidden merge of two component objects"""
    pass


class ComputeStateError(Exception):
    """
    Raised when performing a forbidden calculation of a Component's state field
    """
    pass


class Component(DataModel):
    """
    Common fields for all components
    """
    id = StringType()
    updated_at = ArrowType(default=get_current_ibox_time)
    component_type = StringType()
    _state = EnumType(enum=ComponentState)
    _is_missing = BooleanType(default=False)

    metadata_fields = ['id', '_state', 'state', 'updated_at', '_component_type', 'component_type',
                       '_is_missing', 'is_missing', 'is_missing_field_was_set', 'state_field_was_set', '_data']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.component_type = self._component_type

        # See explanation in function reset_data_collection_cycle
        self.is_missing_field_was_set = False
        self.state_field_was_set = False

    class Options(object):
        """ When comparing - we usually don't want to compare update times"""
        roles = {
            'compare': blacklist('updated_at'),
            'compare_with_updated_at': blacklist(''),
            'clone': blacklist(''),
            'clone_with_updated_at': blacklist('updated_at')
        }

    def __deepcopy__(self, *args):
        """
        Deep copy from self, with new update time

        :return: component tree
        :rtype: ComponentHealthTree
        """
        return self.__class__(self.to_native(role='clone_with_updated_at'))

    def __setattr__(self, name, value):
        super_setattr = super().__setattr__
        super_setattr(name, value)
        if hasattr(self, '_data') and name not in self.metadata_fields:
            super_setattr('updated_at', get_current_ibox_time())

    def fast_import_data(self, data):
        """
        Imports data to the Component quickly, by updating the internal dict - which is substantially faster than
        using setattr on the component object.
        """
        self.set_updated_at_field_to_now()
        self._data.update(data)

    def set_updated_at_field_to_now(self):
        self.updated_at = get_current_ibox_time()

    def __eq__(self, other):
        """
         Comparing two components is performed without accounting for time

        :param other:
        """
        return self.to_native(role='compare') == other.to_native(role='compare')

    def __iter__(self):
        """
        Iterates over the data fields of the Component, skipping over metadata fields (such as 'state' and 'id').
        Returns (name, value) tuple of a field in each iteration.
        """
        return ((name, value) for name, value in self._data.items() if name not in self.metadata_fields)

    def __add__(self, other):
        """
        :param other: Another component of the same type.
        :return: A new Component object, which holds data merged from both this and the other.

        For each field, if one component holds data and the other holds None - the new field will hold the data.
        If for a certain field both components hold different data, an exception will be thrown in order to avoid
        overwritting data.
        """
        if not isinstance(other, self.__class__):
            raise TypeError("Cannot perform merge of a Component and a different type")

        new_merged_component = copy.deepcopy(other)
        other_dict = other.to_native(role='clone')

        for field_name, value in self.to_native('clone').items():
            other_value = other_dict[field_name]

            if value is not None and other_value is not None and value != other_value:
                if field_name == 'updated_at':
                    value = get_latest_time(value, other_value)
                else:
                    raise ComponentMergeError(f"Merging {self} and {other} will cause data of "
                                              f"field '{field_name}' to be overwritten")

            setattr(new_merged_component, field_name, value if value is not None else other_value)

        return new_merged_component

    def __str__(self):
        return str(f"<{self.component_type}: {self.id}>")

    def __repr__(self):
        return str(self)

    def reset_data_collection_cycle(self):
        """
        This function must be run before each monitor cycle - the cycle in which data is collected and rules are
        subsequently run.

        Resets flags that specify whether certain metadata fields have already been set.
        This information is important in order to allow these fields to forbid decreasing their severity during a
        data collection cycle. But the flag must be reset prior to the next cycle.
        """
        self.is_missing_field_was_set = False
        self.state_field_was_set = False

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_value):
        """
        Allows the state severity to decrease only if state_field_was_set flag is False.
        Following this, turns the flag.
        """
        if self._allowed_to_change_locked_field('state', new_value):
            self._state = new_value
            self.state_field_was_set = True

    @property
    def is_missing(self):
        return self._is_missing

    @is_missing.setter
    def is_missing(self, new_value):
        """
        Allows the changing is missing from True to False only if is_missing_field_was_set is False.
        Following this, turns the flag.
        """
        if self._allowed_to_change_locked_field('is_missing', new_value):
            self._is_missing = new_value
            self.is_missing_field_was_set = True

    @property
    def printable_id(self):
        return str(self.id)

    @staticmethod
    def _is_decreasing_field_severity(field_name, current_value, new_value):
        """
        Returns True iff the new value constitutes an decrease in severity from the the old value (which may be
        forbidden).
        This logic is different, depending on the field name.
        Setting None to something else is never a decrease.
        """
        if current_value is None:
            return False

        if field_name == 'state':
            return new_value < current_value
        elif field_name == 'is_missing':
            return current_value is True and new_value is False

    def _allowed_to_change_locked_field(self, field_name, new_value):
        """
        The function return True iff a locked metadata field (i.e self.state and self.is_missing)
        is allowed to change its value to new_value.

        The logic used is as follows:
            * Increasing severity is always allowed (e.g from WARNING to CRITICAL, from is_missing=False
            to is_missing=True or from None to a value)
            * Decreasing severity is only allowed if the flag [component_name].was_set is False, meaning the
             field has yet to be set in this data collection cycle.
        """
        if field_name not in ['state', 'is_missing']:
            raise ValueError(f"Field {field_name} doesn't exists or doesn't require locking mechanism")

        current_value = getattr(self, field_name)
        field_was_set = getattr(self, field_name + '_field_was_set')

        if self._is_decreasing_field_severity(field_name, current_value, new_value) and field_was_set:
            _logger.warning(f"Tried to set field {field_name} of {self} from {current_value} back down to {new_value} "
                            f"in the middle of a data collection cycle")
            return False
        else:
            return True

    def export_metadata_fields(self):
        return {field: getattr(self, field) for field in self.metadata_fields}

    def import_metadata_fields(self, other):
        for field, value in other.export_metadata_fields().items():
            setattr(self, field, value)


class IndependentComponent(Component):
    """
    Component that is not part of any ComponentContainer
    """
    # SystemState will iterate its components according to this priority, with 0 being the lowest
    priority = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = self.__class__.__name__

    @property
    @abstractmethod
    def component_change_message(self):
        """
        Holds the title of the message that will be emitted to the message queue if any data in this component
        container changes.
        """
        return self._component_change_message


class AssociateComponent(Component):
    """
    Component that is always part of a ComponentContainer, and is not accessed independently
    """
    pass


class ComponentContainer(ABC):
    # SystemState will iterate its components according to this priority, with 0 being the lowest
    priority = 0

    @property
    @abstractmethod
    def component_model(self):
        return self._component_model

    @property
    @abstractmethod
    def component_change_message(self):
        """
        Holds the title of the message that will be emitted to the message queue if any data in this component
        container changes.
        """
        return self._component_change_message

    @property
    def component_type(self):
        return self.component_model._component_type

    @property
    def printable_id(self):
        return type(self).__name__

    def set_updated_at_field_to_now(self):
        self.updated_at = get_current_ibox_time()

    def __init__(self, raw_data=None):
        """
        Components are created lazily. If a component with a given key is requested, it is created on the fly.

        Can accept raw_data - which is the dict representation of the data, as produced by to_primitive()
        If passed, uses this data to populate the ComponentContainer. In this case, all components are created
        according to the passed raw data.
        """
        self.state = None
        self.components_dict = defaultdict(self.component_model)
        self.updated_at = get_current_ibox_time()

        if raw_data is not None:
            for key in raw_data:
                self.components_dict[key].import_data(raw_data[key])

    def get_dict(self):
        return self.components_dict

    def to_primitive(self):
        primitive_dict = copy.deepcopy(self.components_dict)
        for key, value in primitive_dict.items():
            primitive_dict[key] = value.to_primitive()

        return primitive_dict

    def __iter__(self):
        return iter(self.components_dict.values())

    def __len__(self):
        return len(self.components_dict)

    def __getitem__(self, key):
        return self.components_dict[key]

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        if self.components_dict.keys() != other.components_dict.keys():
            _logger.warning(f"{self} isn't equal to {other}. They don't have the same component keys")
            return False

        for comp_key in self.components_dict.keys():
            self_component = self.components_dict[comp_key]
            other_component = other.components_dict[comp_key]
            if self_component != other_component:
                _logger.warning(
                    f"{self} isn't equal to {other}, as {self_component} is different from {other_component}")
                return False

        return True

    def difference(self, other_component_container):
        """
        :param other_component_container: Another ComponentContainer instance
        :return: List of all independent components that aren't the same between this
        and the other ComponentContainer instance.
        The list holds tuples of (self_component, other_component) for each difference.
        """
        if not isinstance(other_component_container, ComponentContainer):
            raise TypeError(f"Method '{__name__}' accepts an argument of type {__class__}")

        if self.components_dict.keys() != other_component_container.components_dict.keys():
            _logger.warning(f"{self} and {other_component_container} don't have the same component keys. "
                            f"Returning all keys that aren't shared by both")

            return list((self.components_dict.keys() - other_component_container.components_dict.keys()).union(
                other_component_container.components_dict.keys() - self.components_dict.keys()))

        different_components = []
        for comp_key in self.components_dict.keys():
            self_component = self.components_dict[comp_key]
            other_component = other_component_container.components_dict[comp_key]
            if self_component != other_component:
                different_components.append((self_component, other_component))

        return different_components

    def __add__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError("Cannot perform merge of a ComponentContainer and a different type")

        if len(self) != len(other):
            raise TypeError("Cannot perform merge of ComponentContainers of different sizes")

        new_components_dict = {key: self[key] + other[key] for key in self.components_dict}
        new_component_container = copy.copy(self)
        new_component_container.components_dict = new_components_dict
        return new_component_container

    def __str__(self):
        return str(self.get_dict())

    def __repr__(self):
        return str(self)

    def compute_state(self):
        """
        Runs the compute_state() function of each component contained within the component container.
        Then determines the state of the ComponentContainer by taking the highest (most severe) state of any of the
        contained components.

        Throws an exception if a component doesn't have a state. All components should have states, which are set by
        rules (all of which should have run when infiniguard-health initialized).

        Returns the newly computed state
        """
        most_severe_component_state = ComponentState.NORMAL

        for component in self:
            component_state = component.state

            # TODO: For now, we turned off all generic rules, hence many components don't have a state - so we need
            # TODO: to allow for a state to be None. ComponentContainers that have such missing components will have a
            # TODO: valid state. Need to think about the best way to handle missing components when we return the
            # TODO: generic rules.
            if component_state is not None and component_state >= most_severe_component_state:
                most_severe_component_state = component_state

        self.state = most_severe_component_state
        return self.state

    def reset_data_collection_cycle(self):
        """
        See explanation of this method in the Component level
        """
        for component in self:
            component.reset_data_collection_cycle()


class Chassis(IndependentComponent):
    lc_version = StringType(deserialize_from='Lifecycle Controller Version')  # "Lifecycle Controller": "3.21.21.21",
    idrac_version = StringType(deserialize_from='iDRAC9')  # "iDRAC9": "3.21.21.21 (Build 30)",
    server_admin_version = StringType(deserialize_from='Server Administrator')  # "Server Administrator": "9.1.0",
    bios_version = StringType(deserialize_from='BIOS')  # "BIOS": "1.4.9",
    os_version = StringType(deserialize_from='CentOS Linux'
                            )  # "CentOS Linux": "release 7.5.1804 (Core)  Kernel 3.10.0-862.11.6.el7.x86_64 (x86_64)"

    component_change_message = 'chassis_changed'
    _component_type = 'CHASSIS'


class BMC(IndependentComponent):
    ipmi_ip = IPv4Type(deserialize_from='ip_address')  # "ip_address": "9.151.140.131"
    ipmi_gw_ip = IPv4Type(deserialize_from='ip_gateway')  # "ip_gateway": "9.151.140.200",
    ipmi_ip_source = StringType(deserialize_from='ip_address_source')  # "ip_address_source =  "Static",
    ipmi_subnet = IPv4Type(deserialize_from='ip_subnet')  # "ip_subnet": "255.255.255.0",
    ipmi_mac = StringType(deserialize_from='mac_address')  # "mac_address": "58-8A-5A-FB-23-96",
    sol_enabled = YesNoType(deserialize_from='sol_enabled')  # "sol_enabled": "Yes",
    ipmi_over_lan_enabled = YesNoType(deserialize_from='enable_ipmi_over_lan')  # "enable_ipmi_over_lan": "Yes",

    component_change_message = 'BMC_changed'
    _component_type = 'BMC'


class RaidController(IndependentComponent):
    model = StringType(deserialize_from='name')  # "Dell HBA330 Mini": "15.17.09.06",
    firmware_version = StringType()  # "Dell HBA330 Mini": "15.17.09.06",
    driver_version = StringType()
    status = StringType()

    component_change_message = 'RAID_controller_changed'
    _component_type = 'RAID_CONTROLLER'


class PSU(AssociateComponent):
    product_id = StringType(deserialize_from='product')
    online_status = StringType()
    vendor = StringType()
    firmware_version = StringType()
    serial_number = StringType(deserialize_from='serial')
    capacity = IntType()
    status = StringType()

    _component_type = 'PSU'


class PSUs(ComponentContainer):
    component_model = PSU

    component_change_message = 'PSUs_changed'


class Fan(AssociateComponent):
    rpm = IntType()  # reading
    name = StringType(deserialize_from='probe_name')  # probe_name
    status = StringType()

    _component_type = 'FAN'


class Fans(ComponentContainer):
    component_model = Fan

    component_change_message = 'fans_changed'


class EthInterface(IndependentComponent):
    name = StringType(deserialize_from='interface_name')
    ip_gateway = IPv4Type(deserialize_from='gateway')
    ip_address = IPv4Type()
    netmask = IPv4Type()

    component_change_message = 'eth_interface_changed'
    _component_type = 'ETH_INTERFACE'


class EthPort(AssociateComponent):
    vendor = StringType()  # "vendor": "Intel Corporation",
    model = StringType(deserialize_from='product')  # "product": "Ethernet Controller X710 for 10GbE SFP+",
    serial_number = StringType(deserialize_from='serial')  # "serial": "f8:f2:1e:16:b5:a0",
    firmware_version = StringType(deserialize_from='firmware')  # ['configuration']['firmware']
    driver = StringType()  # ['configuration']['driver']
    driver_version = StringType(deserialize_from='driverversion')  # ['configuration']['driverversion']
    type = StringType(deserialize_from='port')  # ['configuration']['port']
    maximum_speed = StringType()  # syscli
    mtu = IntType()  # syscli
    hardware_revision = StringType(deserialize_from='vendor_rev')  # ethtool -m $$$ - Vendor rev
    vendor_pn = StringType()  # ethtool -m $$$ - Vendor PN
    vendor_sn = StringType()  # ethtool -m $$$ - Vendor SN
    link_state = YesNoType(deserialize_from='link_detected')  # ethtool
    enabled = UpDownType(deserialize_from='connection')  # syscli
    port_name = StringType(deserialize_from='logicalname')  # As displayed in GUI - "logicalname": "p7p1",
    auto_negotiation = OnOffType(deserialize_from='autonegotiation')  # ['configuration']['autonegotiation']
    duplex = StringType()  # ['configuration']['duplex']
    interfaces_count = IntType()  # syscli
    interfaces = ListType(ModelType(EthInterface, strict=False))  # syscl

    _component_type = 'ETH_PORT'

    @property
    def printable_id(self):
        try:
            printable_id = f'DDE{get_local_node_id()}{self.id}'.upper()
        except:
            printable_id = self.id
        return printable_id


class EthernetPorts(ComponentContainer):
    component_model = EthPort

    component_change_message = 'eth_ports_changed'


class BondSlave(IndependentComponent):
    slave_interface = StringType()  # /proc/net/bonding
    mii_status = UpDownType()  # /proc/net/bonding
    speed = StringType()  # /proc/net/bonding
    duplex = StringType()  # /proc/net/bonding
    link_failure_count = StringType()  # /proc/net/bonding

    component_change_message = 'bond_slave_changed'
    _component_type = 'BOND_SLAVE'


class Bond(AssociateComponent):
    driver_version = StringType(deserialize_from='ethernet_channel_bonding_driver')  # /proc/net/bonding
    bonding_mode = StringType()  # /proc/net/bonding
    status = UpDownType(deserialize_from='mii_status')  # /proc/net/bonding
    mii_polling_interval_ms = StringType()  # /proc/net/bonding
    slaves = ListType(ModelType(BondSlave, strict=False))  # /proc/net/bonding

    _component_type = 'BOND'

    @property
    def printable_id(self):
        try:
            printable_id = f'DDE{get_local_node_id()}{self.id}'.upper()
        except:
            printable_id = self.id
        return printable_id


class Bonds(ComponentContainer):
    component_model = Bond

    component_change_message = 'bonds_changed'


class FcPort(AssociateComponent):
    role = StringType()  # gc
    alias = StringType()  # gc
    vendor = StringType()  # lspci_fc
    model = StringType()  # lspci_fc
    serial_number = StringType(deserialize_from='serial_num')  # lspci_fc
    firmware_version = StringType()  # /sys/bus/pci/drivers/qla2xxx*/*/driver/module/version
    slot = StringType(deserialize_from='description')  # gc
    wwn = StringType(deserialize_from='node_name')  # sysfs
    wwpn = StringType(deserialize_from='port_name')  # sysfs
    connection_speed = StringType(deserialize_from='speed')  # sysfs
    hba_info = StringType()  # lspci_fc
    maximum_speed = StringType()  # sysfs?
    hardware_revision = StringType(deserialize_from='engineering_changes')  # lspci_fc
    link_state = UpDownType()  # sysfs
    enabled = YesNoType(deserialize_from='port_state')  # sysfs?
    sfp_supported_speeds = StringType()
    sfp_vendor_name = StringType()
    sfp_vendor_pn = StringType()
    sfp_vendor_revision = StringType()
    sfp_vendor_sn = StringType()

    _component_type = 'FC_PORT'

    @property
    def printable_id(self):
        try:
            printable_id = f'DDE{get_local_node_id()}{self.id}'.upper()
        except:
            printable_id = self.id
        return printable_id


class FcPorts(ComponentContainer):
    component_model = FcPort

    component_change_message = 'fc_ports_changed'


class NIC(IndependentComponent):
    vendor = StringType()
    hardware_revision = StringType()
    model = StringType()
    firmware_version = StringType()
    serial_number = StringType()
    slot = StringType()
    ports = ListType(ModelType(EthPort))

    component_change_message = 'NIC_changed'
    _component_type = 'NIC'


class DIMM(AssociateComponent):
    slot = StringType()
    asset_tag = StringType(deserialize_from='product')
    vendor = StringType()
    part_number = StringType(deserialize_from='handle')
    serial_number = StringType(deserialize_from='serial')
    size = StringType()
    speed = StringType(deserialize_from='clock')
    type = StringType(deserialize_from='description')
    status = StringType()

    _component_type = 'DIMM'


class DIMMs(ComponentContainer):
    component_model = DIMM

    component_change_message = 'DIMMs_changed'


class TempProbe(AssociateComponent):
    probe_name = StringType()
    temp = StringType(deserialize_from='reading')
    status = StringType()

    _component_type = 'TEMPERATURE'


class Temperatures(ComponentContainer):
    component_model = TempProbe

    component_change_message = 'Temperatures_changed'


class Service(AssociateComponent):
    name = StringType()
    status = ActiveInactiveType()

    _component_type = 'SERVICE'


class Services(ComponentContainer):
    component_model = Service

    component_change_message = 'services_changed'


class Volume(AssociateComponent):
    device_name = StringType()
    volume_name = StringType()
    wwid = StringType()
    number_of_active_paths = IntType()

    _component_type = 'VOLUME'

    @property
    def printable_id(self):
        return self.volume_name if self.volume_name else self.id


class Volumes(ComponentContainer):
    component_model = Volume

    component_change_message = 'volumes_changed'


class IboxConnectivity(IndependentComponent):
    is_connected = BooleanType()

    component_change_message = 'ibox_connectivity_changed'
    _component_type = 'IBOX_CONNECTIVITY'


class Role(IndependentComponent):
    role_id = IntType()
    management_ip = IPv4Type()

    component_change_message = 'role_changed'
    _component_type = 'ROLE'


class RemoteDDE(AssociateComponent):
    role = IntType()
    has_ssh_connection = BooleanType()
    ssh_conn_error_msg = StringType()

    _component_type = 'REMOTE_DDE'


class RemoteDDEs(ComponentContainer):
    component_model = RemoteDDE

    component_change_message = 'remote_ddes_changed'


class RemoteIDRAC(AssociateComponent):
    idrac_id = IntType()
    has_redfish_connection = BooleanType()
    redfish_connect_error_msg = StringType()

    _component_type = 'REMOTE_IDRAC'


class RemoteIDRACs(ComponentContainer):
    component_model = RemoteIDRAC

    component_change_message = 'remote_idracs_changed'


class SnapshotsCapacity(IndependentComponent):
    used_snapshot_capacity_percent = FloatType()  # Percent from 0 to 1

    component_change_message = 'snapshots_capacity_changed'
    _component_type = 'SNAPSHOTS_CAPACITY'


class DDECapacity(IndependentComponent):
    used_dde_capacity_percent = FloatType()  # Percent from 0 to 1

    component_change_message = 'dde_capacity_changed'
    _component_type = 'DDE_CAPACITY'


class Policy(AssociateComponent):
    policy_type = StringType()
    enabled = BooleanType()
    frequency = IntType()
    immutable = BooleanType()
    retention = IntType()
    enabled_at = ArrowType()
    latest_frequency_decrease = ArrowType()

    # These fields are populated by a Rule, not a collector
    metadata_fields = Component.metadata_fields + ['enabled_at', 'latest_frequency_decrease']
    _component_type = 'POLICY'


class Policies(ComponentContainer):
    component_model = Policy

    priority = 1  # We want a higher priority than Snapshots, so the snapshot rule will be run after the policy rule
    component_change_message = 'policies_changed'


class Snapshot(AssociateComponent):
    snapshot_id = IntType(deserialize_from='snapid')
    originated_by = StringType()
    created_at = ArrowType()
    expires_at = ArrowType()
    lock_expires_at = ArrowType()  # Received from the snapshot object, not the swagger schema
    ddeapp = StringType()
    label = StringType()
    lock_state = StringType()
    original_policy = ModelType(Policy, deserialize_from='origin')

    _component_type = 'SNAPSHOT'

    def __eq__(self, other):
        """
        When comparing two snapshot objects, we want to have snapshots that are updated at different times to not
        be equal. This is because even if there is no change in the snapshot data, the fact that it was collected later
        might make a rule such as SnapshotOverdue be emited (since more time passed).

        This allows two cycles that are identical in terms of data, but collected in different times, to appear as
        having a difference - which will trigger that snapshot rule and check if (for example) too much time has passed
        and the snapshot is overdue.
        """
        return self.to_native(role='compare_with_updated_at') == other.to_native(role='compare_with_updated_at')


class Snapshots(ComponentContainer):
    component_model = Snapshot

    component_change_message = 'snapshots_changed'

    def __str__(self):
        return self.printable_id

    @staticmethod
    def _get_timestamp_or_epoch_time(timestamp):
        """
        If the given timestamp is None, returns the epoch time (1970) instead. This allows the timestamp to always
        compare as smaller than any other timestamp
        """
        return timestamp or Arrow.fromtimestamp(0)

    def get_ordered_snapshots(self, policy_type):
        """
        Returns a list of all the snapshots of the given type, ordered by their creation time.
        """
        return sorted((snapshot for snapshot in self.components_dict.values()
                       if snapshot.original_policy.policy_type == policy_type),
                      key=lambda snapshot: self._get_timestamp_or_epoch_time(snapshot.created_at))

    @staticmethod
    def _get_index_after_checkpoint(sorted_snapshots, checkpoint_time: Arrow):
        """
        Receives a list of snapshots sorted by their created_at value.
        Returns the index of the first snapshot with a created_at value that is equal or larger to the checkpoint.
        """
        sorted_starting_time = [Snapshots._get_timestamp_or_epoch_time(snapshot.created_at)
                                for snapshot in sorted_snapshots]
        return bisect.bisect_left(sorted_starting_time, checkpoint_time)

    def get_ordered_snapshots_after_checkpoint(self, policy_type, checkpoint_time: Arrow):
        """
        Returns snapshots of the given type with a created_at time that is equal or later than the given
        checkpoint time. Snapshots are ordered according to descending created_at times.
        """
        ordered_snapshots = self.get_ordered_snapshots(policy_type)
        snapshot_index_after_checkpoint = self._get_index_after_checkpoint(ordered_snapshots, checkpoint_time)
        return ordered_snapshots[snapshot_index_after_checkpoint:]

    def prune_deleted_policy_snapshots(self, policy_type, prune_until: Arrow):
        """
        Removes from the infiniguard-health model all snapshots of the given policy that were deleted from the system,
        if their creation time is sooner than the given prune_until time.
        """
        ordered_snapshots = self.get_ordered_snapshots(policy_type)
        first_safe_snapshot_index = self._get_index_after_checkpoint(ordered_snapshots, prune_until)
        snapshots_to_prune = ordered_snapshots[:first_safe_snapshot_index]

        for snapshot in snapshots_to_prune:
            if snapshot.is_missing:
                del self.components_dict[snapshot.snapshot_id]

    def prune_deleted_other_snapshots(self):
        """
        Removes from the infiniguard-health model all snapshots that have been deleted from the system, if they
        are not snapshots that belong to a policy (i.e manual, pre-recover and alien snapshots)
        """
        snapshot_ids_to_delete = []
        for snapshot in self:
            if snapshot.originated_by not in get_default_policy_types() and snapshot.is_missing:
                snapshot_ids_to_delete.append(snapshot.snapshot_id)

        for snapshot_id in snapshot_ids_to_delete:
            del self.components_dict[snapshot_id]

    def __eq__(self, other):
        """
        When comparing two snapshot container objects, we want to have objects that are updated at different times to
        not be equal. This is because even if there is no change in the snapshot data, the fact that it was
        collected later might make a rule such as SnapshotOverdue be emitted (since more time passed).

        When there are snapshots in the container, the regular comparison of Snapshot component objects will take the
        updated_at field into account (see __eq__ of Snapshot). If there are no snapshots, this function returns False
        if the updated_at fields aren't the same.
        """
        if len(self) == 0 and len(other) == 0 and self.updated_at != other.updated_at:
            return False

        return super().__eq__(other)


class SnapshotSuspendDelete(IndependentComponent):
    suspend_delete = BooleanType()

    component_change_message = 'snapshot_suspend_delete_changed'
    _component_type = 'SNAPSHOT_SUSPEND_DELETE'


class SystemState:
    _system_components = {
        SYSTEM_COMPONENT_NAMES.dimms: DIMMs,
        SYSTEM_COMPONENT_NAMES.psus: PSUs,
        SYSTEM_COMPONENT_NAMES.fans: Fans,
        SYSTEM_COMPONENT_NAMES.bmc: BMC,
        SYSTEM_COMPONENT_NAMES.raid_controller: RaidController,
        SYSTEM_COMPONENT_NAMES.ethernet_ports: EthernetPorts,
        SYSTEM_COMPONENT_NAMES.bonds: Bonds,
        SYSTEM_COMPONENT_NAMES.fc_ports: FcPorts,
        SYSTEM_COMPONENT_NAMES.temperatures: Temperatures,
        SYSTEM_COMPONENT_NAMES.services: Services,
        SYSTEM_COMPONENT_NAMES.volumes: Volumes,
        SYSTEM_COMPONENT_NAMES.ibox_connectivity: IboxConnectivity,
        SYSTEM_COMPONENT_NAMES.role: Role,
        SYSTEM_COMPONENT_NAMES.remote_ddes: RemoteDDEs,
        SYSTEM_COMPONENT_NAMES.remote_idracs: RemoteIDRACs,
        SYSTEM_COMPONENT_NAMES.snapshots_capacity: SnapshotsCapacity,
        SYSTEM_COMPONENT_NAMES.dde_capacity: DDECapacity,
        SYSTEM_COMPONENT_NAMES.snapshots: Snapshots,
        SYSTEM_COMPONENT_NAMES.policies: Policies,
        SYSTEM_COMPONENT_NAMES.snapshot_suspend_delete: SnapshotSuspendDelete
    }

    def __init__(self, raw_data=None):
        """
        Can accept raw_data - which is the dict representation of the data, as produced by to_primitive()
        If passed, uses this data to populate the ComponentContainer
        """
        super().__setattr__('state', None)

        if raw_data is None:
            raw_data = {}
        components_dict = {component_key: component_class(raw_data=raw_data.get(component_key))
                           for component_key, component_class in self._system_components.items()}
        super().__setattr__('components_dict', components_dict)
        self.__dict__.update(components_dict)

    def __setattr__(self, key, value):
        if key in self.components_dict:
            self.components_dict[key] = value
        super().__setattr__(key, value)

    def __str__(self):
        return repr(self)

    def __iter__(self):
        """
        Iterates over the components in the system state according to their priority (with 0 being the lowest).
        Since the messages of the message queue (which in turn call the Rules) are called according to this iteration,
        the priorities of the components thus determine the run order of the corresponding rules
        """
        return ((name, element) for name, element in sorted(self.components_dict.items(),
                                                            key=lambda item: item[1].priority, reverse=True))

    def iterate_all_components(self):
        for element in self.components_dict.values():
            if isinstance(element, ComponentContainer):
                yield from element
            else:
                yield element

    def to_primitive(self):
        return {key: value.to_primitive() for key, value in self.components_dict.items()}

    def difference(self, other_system_state):
        """
        :param other_system_state: Another SystemState instance
        :return: List of all components or component containers that aren't the same between this
        and the other SystemState instance. The list holds tuples of (self_item, other_item) for each difference.

        Operates only on the level of components directly held by the SystemState.
        i.e if two individual ports have a difference, will return a list that contains an tuple with
        two the EthernetPorts objects (self_ethernet_ports, other_ethernet_ports).
        In order to obtain the actual ports that are different, you must compare the containers:
        self.ethernet_ports.difference(other_ethernet_ports)
        """
        if not isinstance(other_system_state, SystemState):
            raise TypeError(f"Method '{__name__}' accepts an argument of type {__class__}")

        different_members = []
        for (self_name, self_element), (other_name, other_element) in zip(self, other_system_state):
            if self_element != other_element:
                different_members.append((self_element, other_element))

        return different_members

    def __add__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError("Cannot perform merge of SystemState and a different type")

        new_system_state = copy.deepcopy(self)
        for name, element in self:
            setattr(new_system_state, name, element + getattr(other, name))

        return new_system_state

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        for (_, element), (_, other_element) in zip(self, other):
            if element != other_element:
                _logger.warning(f"{self} isn't equal to {other}, as {element} is different from {other_element}")
                return False

        return True

    def compute_state(self):
        """
        Runs the compute_state() function of each item contained within the SystemState - both ComponentContainers and
        IndependentComponent items.
        Then determines the state of the SystemState by taking the highest (most severe) state of any of the
        contained items.

        Throws an exception if a component doesn't have a state. All components should have states, which are set by
        rules (all of which should have run when infiniguard-health initialized).
        """
        most_severe_component_state = ComponentState.NORMAL

        for name, element in self:
            if isinstance(element, ComponentContainer):
                element_state = element.compute_state()
            else:
                element_state = element.state
                # TODO: This used to raise an exception if the state was None.
                # TODO: Removed it for now, as we are only treating FC and eth ports, and the rest will be None.
                # TODO: When we bring the rest back, need to see if we want to return this raise or just have a test
                # TODO: that makes sure that all components get a state (meaning all rules were correctly defined)

            # TODO: See comment in the ComponentContainer's compute_state
            if element_state is not None and element_state >= most_severe_component_state:
                most_severe_component_state = element_state

        self.state = most_severe_component_state

    def reset_data_collection_cycle(self):
        """
        See explanation of this method in the Component level.
        """
        for _, element in self:
            element.reset_data_collection_cycle()
