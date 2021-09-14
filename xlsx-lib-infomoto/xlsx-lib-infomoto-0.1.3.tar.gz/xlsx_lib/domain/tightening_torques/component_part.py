from domain.tightening_torques.component_part_screw import ComponentPartScrew


class ComponentPart:
    name: str
    screws: list[ComponentPartScrew]

    def __init__(self, name: str):
        self.name = name
        self.screws = list()
