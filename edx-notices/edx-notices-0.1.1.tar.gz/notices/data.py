"""
Public data structures for this app.

See OEP-49 for details
"""
from enum import Enum


class AcknowledgmentResponseTypes(str, Enum):
    """
    Options for the response_type field of a AcknowledgedNotice.
    """

    CONFIRMED = "confirmed"
    DISMISSED = "dismissed"

    @classmethod
    def includes_value(cls, value):
        """Check if the value passed in is a valid option."""
        return value in set(item.value for item in cls)
