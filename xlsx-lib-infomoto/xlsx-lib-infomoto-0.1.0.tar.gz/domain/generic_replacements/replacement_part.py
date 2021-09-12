from dataclasses import dataclass


@dataclass
class ReplacementPart:
    name: str
    reference: str
    observations: str
