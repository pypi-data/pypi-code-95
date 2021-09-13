from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CVE:
    id: str
    name: Optional[str]
    description: Optional[str]
    disclosure_publish_time: Optional[float]
    patch_publish_time: Optional[float]

    def is_patch_available(self) -> bool:
        return self.patch_publish_time is not None
