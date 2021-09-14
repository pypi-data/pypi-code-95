from domain.engine.element_attribute import ElementAttribute


class SectionElement:
    name: str
    value: str
    observations: str
    element_attributes: list[ElementAttribute]

    def __init__(
            self,
            name: str,
            value: str,
            observations: str
    ):
        self.name = name
        self.value = value
        self.observations = observations
        self.element_attributes = list()
