from domain.electronic.component_attribute import ComponentAttribute


class ElementComponent:
    name: str
    value: str
    observations: str
    attributes: list[ComponentAttribute]

    def __init__(
            self,
            name: str,
            value: str,
            observations: str
    ):
        self.name = name
        self.value = value
        self.observations = observations
        self.attributes = list()
