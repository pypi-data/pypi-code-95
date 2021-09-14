from enum import Enum


class SerializerTypes(Enum):
    """
    Types of supported Serializers
    """
    PICKLE = 1
    JSON_PICKLE = 2
