from enum import Enum

"""
EventResolution describes the decision made by the EventEngine regarding a certain EventRequest made.
These are the options:
1. ACCEPTED - The EventRequest was accepted and sent to the InfiniBox.
2. REJECTED - The EventRequest was dropped
3. INCORPORATED - The EventRequest was incorporated, along with some previously rejected EventRequests,
into a single new aggragate event.

Important note - it is the responsibility of the event resolving function to set the resolution of all participating
EventRecords from REJECTED to INCORPORATED
"""
EventResolutionEnum = Enum('EventResolution', ['ACCEPTED', 'REJECTED', 'INCORPORATED'])
