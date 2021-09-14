class ElementPart:
    name: str
    value: str
    observations: str

    def __init__(
            self,
            name: str,
            value: str,
            observations: str
    ):
        self.name = name
        self.value = value
        self.observations = observations
