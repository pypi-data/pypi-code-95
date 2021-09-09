"""
Each of these functions pertain to a certain event type.
All functions must be named in the following pattern: resolve_event_type.
e.g: resolve_dimm_removed, resolve_fan_disabled, etc.

The functions receive an Event instance.
It will also receive a deque object that holds records of the previous
event requests that were made (in the form of an RequestResolutionRecord).

The functions must decide what event should be produced at this point given the available information.
Note that the time of the creation of the event object appears under event.dde_event_timestamp.
The functions return a tuple of (event_to_emit, resolution).
event_to_emit: Event object that represents the new event to be created.
current_resolution: EventResolution enum that defines the resolution of the given EventRequest.
These are the options, and they must be correctly applied:
ACCEPTED - if the function returns the same or a similar Event (as alteration to the event data is possible)
REJECTED - if the function returns None
INCORPORATED - if the function returns a new EventRequest, which incorporates the current EventRequest with
several previous rejected events. Important: in this case it is the responsibility of the function to set the resolution
of all relevant previous event records from REJECTED to INCORPORATED.

Note that for each event type that doesn't have a function here, a default function will be assigned that returns
the same EventRequest that was given, and the resolution ACCEPTED.
"""
