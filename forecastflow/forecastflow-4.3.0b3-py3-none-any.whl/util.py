import datetime
import logging

logger = logging.getLogger(__name__)


# TODO: This file will be too messy, should be refactored.

class ExpirationTimer:
    """
    Manage expiration
    """
    def __init__(self, seconds: int):
        self.seconds = seconds
        self.start = datetime.datetime.now()

    @property
    def is_expired(self) -> bool:
        """
        Returns:
            True if expired
        """
        delta = datetime.datetime.now() - self.start
        if delta.seconds > self.seconds:
            return True
        else:
            return False


def parse_type(type_str: str) -> type:
    """
    Parse type string to python type.
    Use this function to parse type in schema.

    Args:
        type_str:
            Type string like 'float', 'int', ...
    Returns:
        Python native type
    """
    if type_str == 'float':
        return float
    elif type_str == 'int':
        return int
    elif type_str == 'str':
        return str
    elif type_str == 'bool':
        return bool
    else:
        raise ValueError(f"Unsupported type '{type_str}'.")
