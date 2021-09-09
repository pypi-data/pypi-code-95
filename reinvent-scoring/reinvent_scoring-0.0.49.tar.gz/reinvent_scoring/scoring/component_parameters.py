from typing import List
from dataclasses import dataclass


@dataclass
class ComponentParameters:
    component_type: str
    name: str
    weight: float
    model_path: str = None
    specific_parameters: dict = None
