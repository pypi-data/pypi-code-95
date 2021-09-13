from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Fix:
    id: str
    scanner_ids: List[str]
    diagnosis: str
    consequence: str
    solution: str
    url: str
    title: str
    vendor: str
    category: str
    urls: List[str]
    cves: List[str]
    last_update_time: float
    patch_publication_time: float
    number_of_assets: int
    number_of_vulnerabilities: int
    max_vulnerability_score: int
