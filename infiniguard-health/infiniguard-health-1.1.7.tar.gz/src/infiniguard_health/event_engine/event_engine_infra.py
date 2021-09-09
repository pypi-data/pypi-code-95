import logging
from collections import deque
from inspect import getmembers, isfunction, isclass
import gossip
from infiniguard_health.event_engine import event_resolving_functions
from infiniguard_health.event_engine import events as events_module
from infiniguard_health.event_engine.event_resolutions import EventResolutionEnum
from iba_install.core.ibox import get_ibox
from infiniguard_health.utils import Singleton

_logger = logging.getLogger(__name__)

MAX_SAVED_EVENTS = 100


def get_event_types():
    """
    inspects the events module and extracts the event type of all event that are defined there
    """
    event_classes = [member[1] for member in getmembers(events_module,
                                                        lambda member: isclass(member) and
                                                                       events_module.Event in type.mro(member) and
                                                                       member is not events_module.Event)]
    event_types = {event.event_type.default for event in event_classes if event.event_type.default is not None}

    return event_types


class RequestResolutionRecord:
    """
    This class represents the record of a resolved Event request.
    Holds the event object, along with time that the event was initially created. That is, the first time the event
    would have been requested.
    Additionally, holds an EventResolution enum which specifies whether said the event request was granted as is,
    was rejected, or was incorporated into an aggregate event
    (e.g several event requests about link disconnection were incorporated into a single event alerting about
    all of these. In this case all participating EventRecords will hold event_resolution=INCORPORATED)
    """

    def __init__(self, event, request_resolution):
        self.event = event
        self.event_request_time = event.dde_event_timestamp
        self.event_request_resolution = request_resolution

    @property
    def event_type(self):
        return self.event.event_type

    def __str__(self):
        return f"<EventRecord: {self.event_type}, resolution: {self.event_request_resolution}>"


class EventRequestResolver:
    """
    This class in in charge of deciding what action to perform following an event request made by a rule for a
    certain event type.
    Keeps track of the record of previous events and their resolution for of this type of event.
    """

    def __init__(self,
                 event_type,
                 resolver_function,
                 max_saved_events=MAX_SAVED_EVENTS):
        self.event_type = event_type
        self.resolving_function = resolver_function
        self.previous_resolutions_queue = deque(maxlen=max_saved_events)

    def __str__(self):
        return f"<EventRequestResolver: {self.event_type}>"

    def resolve_event_request(self, event):
        """
        Decide, based on the resolving function, what event to emit following the event request.
        If the decision is to not emit an event, returns None.
        Records the request's data for future decision making.
        """
        event_to_emit, request_resolution = self.resolving_function(event, self.previous_resolutions_queue)
        record_of_current_event_request = RequestResolutionRecord(event, request_resolution)
        self.previous_resolutions_queue.append(record_of_current_event_request)

        return event_to_emit


def default_resolver_function(requested_event, resolution_records):
    """
    Used in case there is no custom resolver function defined for a certain event type
    in the module event_resolving_functions.
    """
    return requested_event, EventResolutionEnum.ACCEPTED


class EventEngine(metaclass=Singleton):
    """
    The EventEngine allows all health rules to register an event request.
    It can then resolve all events that were registered - making decisions as to if and how to respond to the request -
    and then send the final events that were decided upon to the InfiniBox.
    Meant to be used as a singleton instance that will be used throughout the health monitor service.
    """

    def __init__(self):
        """
        """
        self._infinibox = get_ibox()

        # Required in order to create DDE events on the system (usually blocked by infinisdk):
        gossip.registry.groups['infinidat.sdk'].set_strict(False)

        self._registered_event_requests = deque()
        self._event_request_resolvers = dict()
        self._approved_events = deque()

        # Event resolving functions is a currently unused feature. All events have the same no-op resolver which
        # automatically accepts all event requests.
        custom_resolver_functions_dict = self._get_event_resolving_functions()

        for event_type in get_event_types():
            if event_type in custom_resolver_functions_dict:
                resolver_function = custom_resolver_functions_dict[event_type]
            else:
                resolver_function = default_resolver_function

            self._event_request_resolvers[event_type] = EventRequestResolver(event_type, resolver_function)

    @staticmethod
    def _get_event_resolving_functions():
        """
        Returns all event resolving functions that appear in the module event_resolving_functions.py, along with their
        relevant event type. This is derived from the functions names, that should be 'resolve_event_type'
        :return: a dict of the form {event_type: resolve_function}
        """
        result = dict()

        for function_name, function in getmembers(event_resolving_functions):
            if isfunction(function):
                prefix, event_type = function_name.split('_', 1)
                event_type = event_type.upper()

                result[event_type] = function

        return result

    def register_event_request(self, event):
        """
        Used by a rule in order to request an event be sent to the InfiniBox.
        When a request is made, the event object is added to the request queue.
        The request may be accepted, rejected or modified - at the discretion of the EventEngine.
        """
        self._registered_event_requests.append(event)

    def register_event_requests(self, events):
        """
        Used by a rule in order to request several events be sent to the InfiniBox.
        """
        self._registered_event_requests.extend(events)

    def resolve_and_emit_infinibox_events(self):
        """
        Resolves all event requests, and sends actual events to the infinibox accordingly.
        All event requests are popped out of the queue, and passed to the relevant resolver.
        After events are resolved, the actual event objects to be emitted are put in the queue event_to_emit.
        If any event creation is unsuccessful, it and all following events are returned to the registered events queue,
        to be emitted next time.
        """

        _logger.debug(f"Resolving event requests and sending events to InfiniBox")
        while self._registered_event_requests:
            requested_event = self._registered_event_requests.popleft()
            event_request_resolver = self._event_request_resolvers[requested_event.event_type]
            approved_event = event_request_resolver.resolve_event_request(requested_event)

            if approved_event:
                self._approved_events.append(approved_event)

        event_sending_stopped = False
        while self._approved_events:
            event_to_emit = self._approved_events.popleft()

            if event_sending_stopped:
                _logger.info(
                    f"Skip sending {event_to_emit} to InfiniBox due to previous connection problem. "
                    f"Will attempt to send again in the next cycle")
                self._registered_event_requests.append(event_to_emit)
            else:
                try:
                    event_to_emit.send_infinibox_event(self._infinibox)
                except events_module.MalformedEventException:
                    _logger.exception(f"Event {event_to_emit} is malformed. Discarding the event.")
                except Exception:
                    _logger.exception(f"Could not create event {event_to_emit} on InfiniBox")
                    self._registered_event_requests.append(event_to_emit)
                    event_sending_stopped = True

    def emit_urgent_event(self, event):
        """
        Emits the given event on the infinibox immediately, bypassing the regular event registration and resolution
        process. Returns the ibox event object.
        """
        _logger.debug(f"Emitting urgent event {event} on ibox immediately.")
        return event.send_infinibox_event(self._infinibox)

    def clear_event_requests(self):
        self._registered_event_requests.clear()
