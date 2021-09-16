# Copyright (c) Qotto, 2021

"""
Record serialization package

Define the interfaces for record serialization.
"""

from eventy.serialization.record_serializer import RecordSerializer
from eventy.serialization.serialization_errors import SerializationError, UnknownRecordTypeError

__all__ = [
    'RecordSerializer',
    'UnknownRecordTypeError',
    'SerializationError',
]
