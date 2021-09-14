from xlsx_lib.domain.json_serializable.custom_json_serializable import JSONSerializable

from xlsx_lib.domain.electronic.element_component import ElementComponent


class ElectronicElement(JSONSerializable):
    def __init__(
            self,
            name: str,
    ):
        self.name: str = name
        self.components: list[ElementComponent] = list()
