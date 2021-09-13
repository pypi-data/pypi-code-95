from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class FixGroup:
    id: str
    name: str
    fix_ids: List[str]
