from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CustomField:
    custom_field_definition_id: int
    name: str
    value: Optional[str]
