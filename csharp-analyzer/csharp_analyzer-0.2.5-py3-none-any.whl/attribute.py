from dataclasses import dataclass


@dataclass
class Attribute:
    Name: str = ''
    Is_class: bool = False
    Is_method: bool = False
