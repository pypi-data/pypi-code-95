from domain.json_serializable.custom_json_serializable import JSONSerializable
from domain.tightening_torques.component_part import ComponentPart


class Component(JSONSerializable):
    name: str
    parts: list[ComponentPart]

    def __init__(self, name: str):
        self.name = name
        self.parts = list()

