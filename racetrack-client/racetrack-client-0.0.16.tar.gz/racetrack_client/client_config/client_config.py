from dataclasses import dataclass, field
from typing import Dict


@dataclass
class ClientConfig:
    """Global options for a local client"""

    # default URL of Racetrack API server (Lifecycle URL)
    lifecycle_url: str = 'http://127.0.0.1:7002'

    # Git auth credentials set for particular repositories
    git_credentials: Dict[str, 'Credentials'] = field(default_factory=dict)

    # Racetrack URL aliases: alias name -> full URL to Lifecycle API
    lifecycle_url_aliases: Dict[str, str] = field(default_factory=dict)


@dataclass
class Credentials:
    username: str
    password: str
