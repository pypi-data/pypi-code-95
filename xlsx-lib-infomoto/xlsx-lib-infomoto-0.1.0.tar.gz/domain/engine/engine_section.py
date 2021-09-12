from domain.json_serializable.custom_json_serializable import JSONSerializable

from domain.engine.section_element import SectionElement


# TODO: Check if JSONSerializable is needed
class EngineSection(JSONSerializable):
    name: str
    section_elements: list[SectionElement]

    def __init__(
            self,
            name: str,
    ):
        self.name = name
        self.section_elements = list()
