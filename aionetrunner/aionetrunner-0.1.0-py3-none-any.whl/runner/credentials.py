from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Credentials:
    username: str
    password: str
    enable: Optional[str] = field(default=None)

    def __post_init__(self):
        if not self.enable:
            self.enable = self.password
