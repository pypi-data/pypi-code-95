"""
Event objects represent an infinibox event from a DDE. The event code at the Infinibox level is DDE_{level}_EVENT
(e.g DDE_INFO_EVENT). In our level, we are splitting these events to several DDE events, each with its own event
type (e.g  FC_PORT_DOWN). Each event type will have its own Event subclass.
Each "actual" event (non abstract class meant for instantiation) must define these two fields:
event_type - the internal code used in our project for event type (e.g FC_PORT_DOWN)
description_template - a template of text that uses the fields of the class. This will be passed (after formatting with
the relevant fields) to the Infinibox event as the {event_desc} fields.

All other fields will be passed to the Inifnibox event as data in the JSON.
"""
import logging
from enum import Enum, auto

from iba_install.lib.ddenode import DdeNode
from schematics.models import Model
from schematics.types import StringType, IntType
from schematics.transforms import blacklist
from schematics.types.compound import ModelType
from tenacity import retry, stop_after_attempt, wait_exponential

from infiniguard_health.blueprints.custom_types import UpDownType, EnumType, PercentageFloatToStringType
from infiniguard_health.blueprints.components import Policy, Snapshot, ComponentContainer
from infiniguard_health.data_collection.sources import get_dde_role
from infiniguard_health.utils import encode_and_compress_for_http, get_epoch_time_milliseconds
from infiniguard_health.utils import get_local_node_id

_logger = logging.getLogger(__name__)

EVENT_RETRY_ATTEMPTS_NUM = 3


class MalformedEventException(Exception):
    pass


class EventLevels(Enum):
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()


class EventVisibility(Enum):
    CUSTOMER = auto()
    INFINIDAT = auto()


class EventReporterType(Enum):
    DDE_NODE = auto()
    DDE_APP = auto()


class Event(Model):
    """
    Abstract - not to be instantiated
    """
    event_type = StringType(required=True)
    description_template = StringType(required=True)
    # Determines whether the event will specify the DDE node or DDE app as the reporter of the event.
    event_reporter_type = EnumType(enum=EventReporterType, required=True)
    level = StringType(required=True)
    visibility = EnumType(enum=EventVisibility, required=True)
    component_type = StringType(required=True)
    component_id = StringType(deserialize_from='printable_id')
    dde_event_timestamp = IntType(default=get_epoch_time_milliseconds)

    fields_to_send_in_data_field = ['event_type', 'component_type', 'component_id', 'dde_event_timestamp',
                                    'event_desc', 'level', 'node_id', 'app_id']

    class Options(object):
        """
        The compare role is used when determining if an event in a new cycle is the same as the
        previous (in which case it should not be emitted again) or different (in which case it should be).
        The timestamp is always different, so it must be ignored, or comparison will always be false.
        """
        roles = {
            'compare': blacklist('dde_event_timestamp'),
        }

    def __init__(self, component=None, **additional_event_parameters):
        """
        Initialization of an event should be via the relevant Component object.
        e.g in order to initialize an EthPortEvent the EthPort object from the components module should be given.
        All relevant fields of the component will be used for the event fields, therefore the field names must match.
        If an event requires fields that cannot be extracted from the component, these must be provided as additional
        kwargs to the initialization. e.g EthPortDownEvent(eth_component, previous_state='UP')
        """
        # Since we can only obtain the component object from within init, we use it within the schematics model by
        # passing it to the primitive_dict and then deserializing from it during the Model's creation
        if component is None:
            primitive_dict = {**additional_event_parameters}

        elif isinstance(component, ComponentContainer):
            primitive_dict = {
                'component_type': component.component_type,
                'printable_id': component.printable_id,
                **additional_event_parameters
            }
        else:
            primitive_dict = {
                **component.to_primitive(),
                **additional_event_parameters,
                'printable_id': component.printable_id
            }

        # Since components have more fields than required by the event (e.g. model name), need to set strict to False
        # for schematics to accept it
        super().__init__(primitive_dict, strict=False)

    def _convert_dict_to_data_parameter(self, fields_dict):
        """
        Receives a dict that contains the data that is to be passed to the HTTP request creating an InfiniBox event.
        Returns the data in the fo rmat required by the InfiniBox: a list of dicts, each representing a single
        field, and in the following format:
        {“type": “the type of the field"(etc’ string’, ‘int’),
          “name”: “the name of the field".
          “value”: "value of the field"
        }
        """
        result = []

        for key, value in fields_dict.items():
            if isinstance(value, int):
                value_type = 'int'
                value = str(value)
            elif isinstance(value, str):
                value_type = 'string'
            elif isinstance(value, float):
                value_type = 'float'
                value = str(value)
            elif type(value) in (list, dict):
                # When passing a list or a dict, InfiniBox protocols requires it encoded and compressed.
                # We sort lists in order to always get the same encoding for a group of items.
                value_type = key
                try:
                    value = encode_and_compress_for_http(value)
                except Exception:
                    raise MalformedEventException(f"Could not encode event value {value} when creating {self}")
            elif value is None:
                value_type = 'string'
                value = 'NONE'
            else:
                raise MalformedEventException(f"Event field {key}:{value} is of wrong type "
                                              f"and cannot be transferred to InfiniBox")

            result.append(
                {
                    'name': key,
                    'type': value_type,
                    'value': value
                }
            )
        return result

    def _get_event_code(self):
        if self.visibility is EventVisibility.INFINIDAT:
            return f'DDE_INTERNAL_{self.level}_EVENT'
        elif self.visibility is EventVisibility.CUSTOMER:
            return f'DDE_{self.level}_EVENT'
        else:
            raise MalformedEventException("Unrecognized event visibility")

    @retry(stop=stop_after_attempt(EVENT_RETRY_ATTEMPTS_NUM), wait=wait_exponential(), reraise=True)
    def send_infinibox_event(self, infinibox):
        """
        Sends the event to the given infiniBox. The InfiniBox event used is DDE_{level}_EVENT
        (depending on the level saved in this event).
        Formats the description according to the template held in the Event object and filled with the data
        in the other fields.

        The data parameter in the HTTP request body contains the following:
        * event_desc: the formatted description as explained above
        * node_id: The given dde_id (physical node).
        * event_type: The event type of this Event (static field).
        * All other fields of the Event object that are to be passed (as listed in self.fields_to_send_in_data_field)

        :param infinibox: An InfiniBox object to which the event should be sent.
        :return The InfiniSdk Event object that represents the event created on the ibox.
        """
        event_code = self._get_event_code()
        event_fields_dict = self.to_primitive()

        # Adding fields to data dict as required by the InfiniBox's DDE event.
        event_fields_dict['node_id'] = get_local_node_id()
        event_fields_dict['app_id'] = get_dde_role()
        event_fields_dict['level'] = self.level
        full_event_template = self._get_event_desc_header() + self.description_template
        event_fields_dict['event_desc'] = full_event_template.format(**event_fields_dict)

        event_data_dict = {key: value for key, value in event_fields_dict.items()
                           if key in self.fields_to_send_in_data_field}
        _logger.debug(f"Send event with code {event_code} and data {event_data_dict} to InfiniBox")
        with infinibox.api.change_request_default_timeout_context(2):
            # TODO: Remove this once infinisim supports the new events
            from infiniguard_health.logger_config import is_test
            if is_test() and 'INTERNAL' in event_code:
                event_code = 'DDE_INTERNAL_EVENT'

            return infinibox.events.create(code=event_code, data=self._convert_dict_to_data_parameter(event_data_dict))

    def _get_event_desc_header(self):
        dde_node = DdeNode(roleid=int(get_dde_role()), nodeid=get_local_node_id())

        if self.event_reporter_type is EventReporterType.DDE_NODE:
            return f'{dde_node}: '
        elif self.event_reporter_type is EventReporterType.DDE_APP:
            return f'{dde_node.app}: '
        else:
            _logger.error(f"Event {self} was created with an invalid reporter type")
            return f'{dde_node}: '

    def __str__(self):
        return f"<DDE EVENT: {self.event_type}>"

    def __eq__(self, other):
        """
         Comparing two components is performed without accounting for the timestamps.
        """
        return self.to_native(role='compare') == other.to_native(role='compare')


class ComponentNotFoundEvent(Event):
    # Static fields
    event_type = StringType(default='COMPONENT_NOT_FOUND')
    level = StringType(default=EventLevels.ERROR.name)
    visibility = EnumType(enum=EventVisibility, default=EventVisibility.INFINIDAT)
    description_template = StringType(default="Component {component_type} {component_id} not found in system")
    event_reporter_type = EnumType(enum=EventReporterType, default=EventReporterType.DDE_NODE)


class MissingData(Event):
    # Static fields
    event_type = StringType(default='COMPONENT_DATA_MISSING')
    level = StringType(default=EventLevels.ERROR.name)
    visibility = EnumType(enum=EventVisibility, default=EventVisibility.INFINIDAT)
    description_template = StringType(default="No data found for for field '{field_name}' of {component_type}. Unable "
                                              "to monitor this component.")
    event_reporter_type = EnumType(enum=EventReporterType, default=EventReporterType.DDE_APP)

    # To be given manually at event instantiation
    field_name = StringType(required=True)


class EthPortLinkChangeEvent(Event):
    """
    Abstract - not to be instantiated
    """
    description_template = StringType(default="Ethernet port {component_id} is {current_state}")
    event_reporter_type = EnumType(enum=EventReporterType, default=EventReporterType.DDE_NODE)

    # Filled automatically via the component at instantiation
    current_state = UpDownType(required=True, deserialize_from='link_state')


class FrontendEthPortDownEvent(EthPortLinkChangeEvent):
    event_type = StringType(default='FRONTEND_ETH_PORT_DOWN')
    level = StringType(default=EventLevels.ERROR.name)
    visibility = EnumType(enum=EventVisibility, default=EventVisibility.CUSTOMER)


class FrontendEthPortUpEvent(EthPortLinkChangeEvent):
    event_type = StringType(default='FRONTEND_ETH_PORT_UP')
    level = StringType(default=EventLevels.INFO.name)
    visibility = EnumType(enum=EventVisibility, default=EventVisibility.CUSTOMER)


class BackendEthPortDownEvent(EthPortLinkChangeEvent):
    event_type = StringType(default='BACKEND_ETH_PORT_DOWN')
    level = StringType(default=EventLevels.ERROR.name)
    visibility = EnumType(enum=EventVisibility, default=EventVisibility.INFINIDAT)


class BackendEthPortUpEvent(EthPortLinkChangeEvent):
    event_type = StringType(default='BACKEND_ETH_PORT_UP')
    level = StringType(default=EventLevels.INFO.name)
    visibility = EnumType(enum=EventVisibility, default=EventVisibility.INFINIDAT)


class EthPortSpeedChangeEvent(Event):
    """
    Abstract - not to be instantiated
    """
    # Static fields
    level = StringType(default=EventLevels.INFO.name)
    description_template = StringType(default="Maximal speed of Ethernet port {component_id} has changed from "
                                              "{previous_speed} to {current_speed}")
    event_reporter_type = EnumType(enum=EventReporterType, default=EventReporterType.DDE_NODE)

    # Filled via the component at instantiation
    current_speed = StringType(required=True, deserialize_from='maximum_speed')

    # To be given manually at event instantiation, if previous state exists
    previous_speed = StringType(required=True)


class BackendEthPortSpeedChangeEvent(EthPortSpeedChangeEvent):
    event_type = StringType(default='BACKEND_ETH_PORT_SPEED_CHANGED')
    visibility = EnumType(enum=EventVisibility, default=EventVisibility.INFINIDAT)


class FrontendEthPortSpeedChangeEvent(EthPortSpeedChangeEvent):
    event_type = StringType(default='FRONTEND_ETH_PORT_SPEED_CHANGED')
    visibility = EnumType(enum=EventVisibility, default=EventVisibility.INFINIDAT)


class BondStatusChangeEvent(Event):
    """
    Abstract - not to be instantiated
    """
    description_template = StringType(default="Bond {component_id} is {current_status}")
    visibility = EnumType(enum=EventVisibility, default=EventVisibility.CUSTOMER)
    event_reporter_type = EnumType(enum=EventReporterType, default=EventReporterType.DDE_NODE)

    # Filled automatically via the component at instantiation
    current_status = UpDownType(required=True, deserialize_from='status')


class BondDownEvent(BondStatusChangeEvent):
    event_type = StringType(default='BOND_DOWN')
    level = StringType(default=EventLevels.ERROR.name)


class BondUpEvent(BondStatusChangeEvent):
    event_type = StringType(default='BOND_UP')
    level = StringType(default=EventLevels.INFO.name)


class FCPortLinkChangeEvent(Event):
    """
    Abstract - not to be instantiated
    """
    description_template = StringType(default="FC port {component_id} is {current_state}")
    event_reporter_type = EnumType(enum=EventReporterType, default=EventReporterType.DDE_NODE)

    # Filled automatically via the component at instantiation
    current_state = UpDownType(required=True, deserialize_from='link_state')


class FrontendFCPortDownEvent(FCPortLinkChangeEvent):
    event_type = StringType(default='FRONTEND_FC_PORT_DOWN')
    level = StringType(default=EventLevels.ERROR.name)
    visibility = EnumType(enum=EventVisibility, default=EventVisibility.CUSTOMER)


class FrontendFCPortUpEvent(FCPortLinkChangeEvent):
    event_type = StringType(default='FRONTEND_FC_PORT_UP')
    level = StringType(default=EventLevels.INFO.name)
    visibility = EnumType(enum=EventVisibility, default=EventVisibility.CUSTOMER)


class BackendFCPortDownEvent(FCPortLinkChangeEvent):
    event_type = StringType(default='BACKEND_FC_PORT_DOWN')
    level = StringType(default=EventLevels.WARNING.name)
    visibility = EnumType(enum=EventVisibility, default=EventVisibility.INFINIDAT)


class BackendFCPortUpEvent(FCPortLinkChangeEvent):
    event_type = StringType(default='BACKEND_FC_PORT_UP')
    level = StringType(default=EventLevels.INFO.name)
    visibility = EnumType(enum=EventVisibility, default=EventVisibility.INFINIDAT)


# ======= To use when the role of the FC port cannot be determined from the data ======
class UndefinedFCPortDownEvent(FCPortLinkChangeEvent):
    event_type = StringType(default='FC_PORT_DOWN')
    level = StringType(default=EventLevels.WARNING.name)
    visibility = EnumType(enum=EventVisibility, default=EventVisibility.CUSTOMER)


class UndefinedFCPortUpEvent(FCPortLinkChangeEvent):
    event_type = StringType(default='FC_PORT_UP')
    level = StringType(default=EventLevels.INFO.name)
    visibility = EnumType(enum=EventVisibility, default=EventVisibility.CUSTOMER)


class FCPortSpeedChangeEvent(Event):
    """
    Abstract - not to be instantiated
    """
    # Static fields
    level = StringType(default=EventLevels.INFO.name)
    description_template = StringType(default="Connection speed of FC port {component_id} has changed from "
                                              "{previous_speed} to {current_speed}")
    visibility = EnumType(enum=EventVisibility, default=EventVisibility.INFINIDAT)
    event_reporter_type = EnumType(enum=EventReporterType, default=EventReporterType.DDE_NODE)

    # Filled via the component at instantiation
    current_speed = StringType(required=True, deserialize_from='connection_speed')

    # To be given manually at event instantiation, if previous state exists
    previous_speed = StringType(required=True)


class BackendFCPortSpeedChangeEvent(FCPortSpeedChangeEvent):
    event_type = StringType(default='BACKEND_FC_PORT_SPEED_CHANGED')


class FrontendFCPortSpeedChangeEvent(FCPortSpeedChangeEvent):
    event_type = StringType(default='FRONTEND_FC_PORT_SPEED_CHANGED')


# To use when the role of the FC port cannot be determined from the data
class UndefinedFCPortSpeedChangeEvent(FCPortSpeedChangeEvent):
    event_type = StringType(default='FC_PORT_SPEED_CHANGED')


class SnapshotCapacityEvent(Event):
    visibility = EnumType(enum=EventVisibility, default=EventVisibility.CUSTOMER)
    event_reporter_type = EnumType(enum=EventReporterType, default=EventReporterType.DDE_APP)

    # Filled via the component at instantiation
    used_snapshot_capacity_percent = PercentageFloatToStringType()


class SnapshotCapacityNormal(SnapshotCapacityEvent):
    level = StringType(default=EventLevels.INFO.name)
    event_type = StringType(default='SNAPSHOT_CAPACITY_NORMAL')
    description_template = StringType(
        default='Capacity reserved for snapshots is {used_snapshot_capacity_percent} full')


class SnapshotCapacityLimited(SnapshotCapacityEvent):
    level = StringType(default=EventLevels.WARNING.name)
    event_type = StringType(default='SNAPSHOT_CAPACITY_LIMITED')
    description_template = StringType(
        default='Capacity reserved for snapshots is {used_snapshot_capacity_percent} full')


class SnapshotCapacityCritical(SnapshotCapacityEvent):
    level = StringType(default=EventLevels.CRITICAL.name)
    event_type = StringType(default='SNAPSHOT_CAPACITY_CRITICAL')
    description_template = StringType(
        default='Capacity reserved for snapshots is {used_snapshot_capacity_percent} full. '
                'Immediate action to free space is required')


class SnapshotCapacityDepleted(SnapshotCapacityEvent):
    level = StringType(default=EventLevels.CRITICAL.name)
    event_type = StringType(default='SNAPSHOT_CAPACITY_DEPLETED')
    description_template = StringType(
        default='Capacity reserved for snapshots is {used_snapshot_capacity_percent} full. '
                'Immediate action to free space is required. No additional snapshots can be taken')


class DDECapacityEvent(Event):
    visibility = EnumType(enum=EventVisibility, default=EventVisibility.CUSTOMER)
    event_reporter_type = EnumType(enum=EventReporterType, default=EventReporterType.DDE_APP)


class DDECapacityNormal(DDECapacityEvent):
    level = StringType(default=EventLevels.INFO.name)
    event_type = StringType(default='DDE_CAPACITY_NORMAL')
    description_template = StringType(
        default='DDE capacity usage is below {capacity_is_below}%')

    # To be given manually at event instantiation
    capacity_is_below = IntType(required=True)


class DDECapacityWarning(DDECapacityEvent):
    level = StringType(default=EventLevels.WARNING.name)
    event_type = StringType(default='DDE_CAPACITY_WARNING')
    description_template = StringType(
        default='DDE capacity threshold of {capacity_exceeded}% exceeded')

    # To be given manually at event instantiation
    capacity_exceeded = IntType(required=True)


class NegativeSnapshotEvent(Event):
    visibility = EnumType(enum=EventVisibility, default=EventVisibility.INFINIDAT)
    event_reporter_type = EnumType(enum=EventReporterType, default=EventReporterType.DDE_APP)
    level = StringType(default=EventLevels.CRITICAL.name)


class SnapshotNotDeletedEvent(NegativeSnapshotEvent):
    event_type = StringType(default='CYBER_RECOVERY_SNAPSHOT_NOT_DELETED')
    description_template = StringType(
        default='Cyber recovery monitoring failure - Snapshot {component_id} was set to expire at {expires_at}, but'
                ' it still exists in the system. This may indicate a failure in the Cyber Recovery service, or a '
                'possible attack.')

    # Filled via the component at instantiation
    expires_at = StringType(required=True)


class SnapshotBadExpirationValue(NegativeSnapshotEvent):
    event_type = StringType(default='CYBER_RECOVERY_SNAPSHOT_BAD_EXPIRATION_VALUE')
    description_template = StringType(
        default='Cyber recovery monitoring failure - Snapshot {component_id} has a faulty expired_at value'
                ' ({expires_at}). The snapshot was created at {created_at} with a retention value of '
                '{original_policy[retention]} days.')

    # Filled via the component at instantiation
    expires_at = StringType(required=True)
    created_at = StringType(required=True)
    original_policy = ModelType(Policy, required=True)


class SnapshotBadCreationValue(NegativeSnapshotEvent):
    event_type = StringType(default='CYBER_RECOVERY_SNAPSHOT_BAD_CREATION_VALUE')
    description_template = StringType(
        default='Cyber recovery monitoring failure - Snapshot {component_id} has '
                'no created_at value.')


class SnapshotWrongLock(NegativeSnapshotEvent):
    event_type = StringType(default='CYBER_RECOVERY_SNAPSHOT_WRONG_LOCK')
    description_template = StringType(
        default="Cyber recovery monitoring failure - Snapshot {component_id} should be locked according to its policy, "
                "yet the expires_at field ({expires_at}) is not equal to the expiration of the snapshot's lock "
                "({lock_expires_at}). This may indicate a failure in the Cyber Recovery service, or a "
                "possible attack.")

    # Filled via the component at instantiation
    expires_at = StringType(required=True)
    lock_expires_at = StringType(required=True)


class SnapshotIsLocked(NegativeSnapshotEvent):
    event_type = StringType(default='CYBER_RECOVERY_SNAPSHOT_IS_LOCKED')
    description_template = StringType(
        default="Cyber recovery monitoring failure - Snapshot {component_id} has an active lock (which expires at "
                "{lock_expires_at}), yet according to the snapshot policy the snapshot should be unlocked. "
                "This may indicate a failure in the Cyber Recovery service, or a possible attack.")

    # Filled via the component at instantiation
    lock_expires_at = StringType(required=True)


# The following snapshot events operate on all snapshots together, and therefore will receive the component container
# upon instantiation, not an individual snapshot

class AllSnapshotsPositiveEvent(Event):
    visibility = EnumType(enum=EventVisibility, default=EventVisibility.INFINIDAT)
    event_reporter_type = EnumType(enum=EventReporterType, default=EventReporterType.DDE_APP)
    level = StringType(default=EventLevels.INFO.name)

    event_type = StringType(default='CYBER_RECOVERY_ALL_SNAPSHOTS_DATA_OK')
    description_template = StringType(
        default='Cyber recovery monitoring - The data of all DDE snapshots in the system is OK.')


class SnapshotOverdue(NegativeSnapshotEvent):
    event_type = StringType(default='CYBER_RECOVERY_SNAPSHOT_OVERDUE')
    description_template = StringType(
        default='Cyber recovery monitoring failure - Snapshots of active policy "{current_policy[policy_type]}" have '
                'not been taken in the last {delay_minutes} minutes, although the frequency of the policy is set to '
                '{current_policy[frequency]} hours. This may indicate a failure in the Cyber Recovery'
                ' service, or a possible attack.')

    # To be given manually at event instantiation
    current_policy = ModelType(Policy)
    delay_minutes = IntType()

    class Options(object):
        """
        The compare role is used when determining if an event in a new cycle is the same as the
        previous (in which case it should not be emitted again) or different (in which case it should be).
        The timestamp is always different, so it must be ignored, or comparison will always be false.

        For the SnapshotOverdue event, delay_minutes changes as the time advances, and we don't want new events to be
        emitted each time the delay_minutes increases. So we're ignoring it in the comparison.
        """
        roles = {
            'compare': blacklist('dde_event_timestamp', 'delay_minutes'),
        }


class SnapshotWrongFrequency(NegativeSnapshotEvent):
    event_type = StringType(default='CYBER_RECOVERY_SNAPSHOT_WRONG_FREQUENCY')
    description_template = StringType(
        default='Cyber recovery monitoring failure - Snapshot {bad_snapshot[id]} of '
                '"{bad_snapshot[original_policy][policy_type]}" was taken {time_difference_minutes} minutes after '
                'the previous snapshot ({previous_snapshot[id]}). This is inconsistent with the frequency of '
                '{bad_snapshot[original_policy][frequency]} hours defined by the policy at the time. It may indicate a '
                'failure in the Cyber Recovery service, or a possible attack.')

    # To be given manually at event instantiation
    bad_snapshot = ModelType(Snapshot)
    previous_snapshot = ModelType(Snapshot)
    time_difference_minutes = IntType()


class NumSnapshotsOk(Event):
    visibility = EnumType(enum=EventVisibility, default=EventVisibility.CUSTOMER)
    event_reporter_type = EnumType(enum=EventReporterType, default=EventReporterType.DDE_APP)
    level = StringType(default=EventLevels.INFO.name)

    event_type = StringType(default='NUM_SNAPSHOTS_OK')
    description_template = StringType(default='The number of snapshots in the system is valid. '
                                              'Limit of {snapshots_num_limit} snapshots has not been reached.')

    # To be given manually at event instantiation
    snapshots_num_limit = IntType()


class SnapshotsNumHigh(Event):
    visibility = EnumType(enum=EventVisibility, default=EventVisibility.CUSTOMER)
    event_reporter_type = EnumType(enum=EventReporterType, default=EventReporterType.DDE_APP)
    level = StringType(default=EventLevels.WARNING.name)
    event_type = StringType(default='NUM_SNAPSHOTS_HIGH')
    description_template = StringType(default='The system has reached {snapshots_num_percent_reached}% of the number '
                                              'of snapshots allowed ({snapshots_num_limit}). '
                                              'You may remove user snapshots to accommodate more system snapshots.')

    # To be given manually at event instantiation
    snapshots_num_percent_reached = IntType()
    snapshots_num_limit = IntType()


class SnapshotsNumDangerous(Event):
    visibility = EnumType(enum=EventVisibility, default=EventVisibility.CUSTOMER)
    event_reporter_type = EnumType(enum=EventReporterType, default=EventReporterType.DDE_APP)
    # TODO: Are we sure this is also WARNING, not ERROR? (90%)
    level = StringType(default=EventLevels.WARNING.name)
    event_type = StringType(default='NUM_SNAPSHOTS_DANGEROUS')
    description_template = StringType(default='The system has reached {snapshots_num_percent_reached}% of the number '
                                              'of snapshots allowed ({snapshots_num_limit}). '
                                              'You may remove user snapshots to accommodate more system snapshots.')

    # To be given manually at event instantiation
    snapshots_num_percent_reached = IntType()
    snapshots_num_limit = IntType()


class SnapshotsNumCritical(Event):
    visibility = EnumType(enum=EventVisibility, default=EventVisibility.CUSTOMER)
    event_reporter_type = EnumType(enum=EventReporterType, default=EventReporterType.DDE_APP)
    level = StringType(default=EventLevels.CRITICAL.name)
    event_type = StringType(default='NUM_SNAPSHOTS_CRITICAL')
    description_template = StringType(default='The system has reached {snapshots_num_percent_reached}% of the number '
                                              'of snapshots allowed ({snapshots_num_limit}). '
                                              'You may remove user snapshots to accommodate more system snapshots.')

    # To be given manually at event instantiation
    snapshots_num_percent_reached = IntType()
    snapshots_num_limit = IntType()


class SnapshotsNumDepleted(Event):
    visibility = EnumType(enum=EventVisibility, default=EventVisibility.CUSTOMER)
    event_reporter_type = EnumType(enum=EventReporterType, default=EventReporterType.DDE_APP)
    level = StringType(default=EventLevels.CRITICAL.name)
    event_type = StringType(default='NUM_SNAPSHOTS_DEPLETED')
    description_template = StringType(default='The system has reached the limit of the number of snapshots '
                                              'allowed ({snapshots_num_limit}). System snapshots will no longer be '
                                              'taken, and new data is not protected. You may remove user snapshots '
                                              'to accommodate more system snapshots.')

    # To be given manually at event instantiation
    snapshots_num_limit = IntType()


# =========== INFINIGUARD_HEALTH_FAILURE_EVENTS ================
class InfiniguardHealthDataCollectionError(Event):
    visibility = EnumType(enum=EventVisibility, default=EventVisibility.INFINIDAT)
    event_reporter_type = EnumType(enum=EventReporterType, default=EventReporterType.DDE_APP)
    level = StringType(default=EventLevels.ERROR.name)
    event_type = StringType(default='INFINIGUARD_HEALTH_DATA_COLLECTION_ERROR')
    description_template = StringType(default='The infiniguard_health service encountered an exception during '
                                              'the data collection of {loader_name} . Exception: {exception_string}')

    # To be given manually at event instantiation
    exception_string = StringType(required=True)
    loader_name = StringType(required=True)


class InfiniguardHealthFatalException(Event):
    visibility = EnumType(enum=EventVisibility, default=EventVisibility.INFINIDAT)
    event_reporter_type = EnumType(enum=EventReporterType, default=EventReporterType.DDE_APP)
    level = StringType(default=EventLevels.CRITICAL.name)
    event_type = StringType(default='INFINIGUARD_HEALTH_FATAL_EXCEPTION')
    description_template = StringType(default='The infiniguard_health service encountered a fatal exception, causing '
                                              'it to crash. Exception: {exception_string}')

    # To be given manually at event instantiation
    exception_string = StringType(required=True)


# TODO: All these events exists but are not part of the current version.
# TODO: When we bring them back, need to make sure that they all conform product's event requirement (including the
# TODO: correct visibility)
# class PSUEvent(Event):
#     """
#     Abstract - not to be instantiated
#     """
#
#
# class PSUDownEvent(PSUEvent):
#     """
#     This is event is to be used only when initiating the system and discovering that the PSU is down - if there
#     is no previous data to compare to.
#
#     Usage example: PSUDownEvent(psu_component)
#     """
#     # Static fields
#     event_type = StringType(default='PSU_DOWN')
#     level = StringType(default=EventLevels.ERROR.name)
#     description_template = StringType(default="PSU {component_id} - Status is {current_status}.")
#     # Filled automatically via the component at instantiation
#     current_status = StringType(required=True, deserialize_from='status')
#
#
# class PSUUpToDownEvent(PSUDownEvent):
#     """
#     Usage example: PSUUpToDownEvent(psu_component, previous_state='Ok')
#     """
#     # To be given manually at event instantiation, if previous state exists
#     previous_status = StringType(required=True)
#
#     description_template = StringType(default="PSU {component_id} - Status has changed from {previous_status}"
#                                               " to {current_status}.")
#
#
# class PSUDownToUpEvent(PSUEvent):
#     """
#     Usage example: PSUDownToUpEvent(psu_component, previous_state='Critical')
#     """
#     # Static fields
#     event_type = StringType(default='PSU_UP')
#     level = StringType(default=EventLevels.INFO.name)
#     description_template = StringType(default="PSU {component_id} - Status has changed from {previous_status}"
#                                               " to {current_status}.")
#
#     # Filled via the component at instantiation
#     current_status = StringType(required=True, deserialize_from='status')
#
#     # To be given manually at event instantiation, if previous state exists
#     previous_status = StringType(required=True)
#
#
# class DIMMEvent(Event):
#     """
#     Abstract - not to be instantiated
#     """
#
#
# class DIMMDownEvent(DIMMEvent):
#     """
#     This is event is to be used only when initiating the system and discovering that the DIMM is down - if there
#     is no previous data to compare to.
#
#     Usage example: DIMMDownEvent(dimm_component)
#     """
#     # Static fields
#     event_type = StringType(default='DIMM_DOWN')
#     level = StringType(default=EventLevels.WARNING.name)
#     description_template = StringType(default="DIMM {component_id} - Status is {current_status}.")
#     # Filled automatically via the component at instantiation
#     current_status = StringType(required=True, deserialize_from='status')
#
#
# class DIMMUpToDownEvent(DIMMDownEvent):
#     """
#     Usage example: DIMMUpToDownEvent(psu_component, previous_state='Ok')
#     """
#     # To be given manually at event instantiation, if previous state exists
#     previous_status = StringType(required=True)
#
#     description_template = StringType(default="DIMM {component_id} - Status has changed from {previous_status}"
#                                               " to {current_status}.")
#
#
# class DIMMDownToUpEvent(DIMMEvent):
#     """
#     Usage example: DIMMDownToUpEvent(dimm_component, previous_state='Critical')
#     """
#     # Static fields
#     event_type = StringType(default='DIMM_UP')
#     level = StringType(default=EventLevels.INFO.name)
#     description_template = StringType(default="DIMM {component_id} - Status has changed from {previous_status}"
#                                               " to {current_status}.")
#
#     # Filled via the component at instantiation
#     current_status = StringType(required=True, deserialize_from='status')
#
#     # To be given manually at event instantiation, if previous state exists
#     previous_status = StringType(required=True)
#
#
# class FanEvent(Event):
#     """
#     Abstract - not to be instantiated
#     """
#
#
# class FanLowSpeedEvent(FanEvent):
#     """
#     Abstract - not to be instantiated.
#     Meant to be inherited by events used during the initialization of the system and discovering that the
#     Fan is in an invalid state - if there is no previous data to compare to.
#     """
#     # Static fields
#     description_template = StringType(default="Fan {component_id} - Speed is {current_speed} RPM."
#                                               " Status is {current_status}.")
#     # Filled automatically via the component at instantiation
#     current_status = StringType(required=True, deserialize_from='status')
#     current_speed = IntType(required=True, deserialize_from='rpm')
#
#
# class FanLowSpeedWarning(FanLowSpeedEvent):
#     """
#     To be used when initializing the system and discovering that the Fan's speed is below the warning level.
#
#     Usage example: FanLowSpeedWarning(fan_component)
#     """
#     event_type = StringType(default='FAN_LOW_SPEED_WARNING')
#     level = StringType(default=EventLevels.WARNING.name)
#
#
# class FanLowSpeedError(FanLowSpeedEvent):
#     """
#     To be used when initializing the system and discovering that the Fan's speed is below the warning level.
#
#     Usage example: FanLowSpeedError(fan_component)
#     """
#     event_type = StringType(default='FAN_LOW_SPEED_ERROR')
#     level = StringType(default=EventLevels.ERROR.name)
#
#
# class FanOkToLowSpeedWarning(FanLowSpeedWarning):
#     """
#     To be used when older data exists.
#
#     Usage example: FanOkToLowSpeedWarning(fan_component, previous_state='Ok', previous_speed=10440)
#     """
#
#     # To be given manually at event instantiation, if previous state exists
#     previous_status = StringType(required=True)
#     previous_speed = IntType(required=True)
#
#     description_template = StringType(default="Fan {component_id} - Speed has changed from {previous_speed} RPM"
#                                               " to {current_speed} RPM. Status is {current_status}.")
#
#
# class FanOkToLowSpeedError(FanLowSpeedError):
#     """
#     To be used when older data exists.
#
#     Usage example: FanOkToLowSpeedError(fan_component, previous_state='Ok', previous_speed=10440)
#     """
#
#     # To be given manually at event instantiation, if previous state exists
#     previous_status = StringType(required=True)
#     previous_speed = IntType(required=True)
#
#     description_template = StringType(default="Fan {component_id} - Speed has changed from {previous_speed} RPM"
#                                               " to {current_speed} RPM. Status is {current_status}.")
#
#
# class FanErrorToOkEvent(FanEvent):
#     """
#     To be used when fan moves from invalid to valid state.
#
#     Usage example: FanErrorToOkEvent(fan_component, previous_state='Critical', previous_speed=200)
#     """
#     # Static fields
#     event_type = StringType(default='FAN_NORMAL')
#     level = StringType(default=EventLevels.INFO.name)
#     description_template = StringType(default="Fan {component_id} - Speed has changed from {previous_speed} RPM"
#                                               " to {current_speed} RPM. Status is {current_status}.")
#     # Filled via the component at instantiation
#     current_status = StringType(required=True, deserialize_from='status')
#     current_speed = IntType(required=True, deserialize_from='rpm')
#
#     # To be given manually at event instantiation, if previous state exists
#     previous_status = StringType(required=True)
#     previous_speed = IntType(required=True)
