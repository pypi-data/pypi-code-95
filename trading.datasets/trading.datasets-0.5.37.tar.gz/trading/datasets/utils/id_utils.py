"""Module containing ID-generation utility functions."""

import uuid


def generate_uuid(input_text):
    """Returns a random UUID given an input text."""
    return uuid.uuid5(uuid.NAMESPACE_OID, input_text).hex
