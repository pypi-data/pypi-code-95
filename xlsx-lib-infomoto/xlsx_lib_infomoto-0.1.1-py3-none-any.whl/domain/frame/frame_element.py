from typing import Union

from domain.json_serializable.custom_json_serializable import JSONSerializable


# TODO: Check if JSONSerializable is needed
class FrameElement(JSONSerializable):
    def __init__(
            self,
            name: str,
            value: str,
            observations: Union[str, list[str]],
    ):
        self.name: str = name
        self.value: str = value
        self.observations: Union[str, list[str]] = observations
        self.element_parts = list()
