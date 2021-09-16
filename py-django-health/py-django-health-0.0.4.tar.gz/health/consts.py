import enum


class Status(enum.Enum):
    """
    Status Enum
    """
    DEAD = 'DEAD'
    ALIVE = 'ALIVE'
    UNKNOWN = 'UNKNOWN'
