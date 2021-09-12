import random
from typing import Optional, IO

from domain.engine.engine_section import EngineSection
from domain.frame.frame_element import FrameElement
from domain.json_serializable.custom_json_serializable import JSONSerializable

from domain.generic_replacements.replacement import Replacement
from domain.tightening_torques.component import Component
from domain.electronic.electronic_element import ElectronicElement


class MotorcycleModel(JSONSerializable):
    def __init__(
            self,
            model_name: str,
            generic_replacements: Optional[list[Replacement]] = None,
            components_screws_tightening_torques: Optional[list[Component]] = None,
            electronic_elements: Optional[list[ElectronicElement]] = None,
            engine_sections: Optional[list[EngineSection]] = None,
            frame_elements: Optional[list[FrameElement]] = None,
            directory_name: Optional[str] = None,
    ):
        self.model_name: str = model_name
        self.generic_replacements: Optional[list[Replacement]] = generic_replacements
        self.components_screws_tightening_torques: Optional[list[Component]] = components_screws_tightening_torques
        self.electronic_elements: Optional[list[ElectronicElement]] = electronic_elements
        self.engine_sections: list[EngineSection] = engine_sections
        self.frame_elements: Optional[list[FrameElement]] = frame_elements

        json_text: str = self.to_json()

        path: str

        if directory_name is not None:
            path = f"{directory_name}/{self.model_name}.json"
        else:
            path = f"./xlsx_lib/json/{random.randint(0, 999)}.json"

        file: IO = open(path, "w")
        file.write(json_text)
        file.close()
