from abc import ABC, abstractmethod
from typing import List, Optional

import clicasso
import miniscule

from apparatus.config import Config


class Command(clicasso.BaseCommand, ABC):
    @abstractmethod
    def run(self, config: Config, remainder: List[str]) -> None:
        pass


def read_repo_config(config: Config, env: Optional[str]):
    if env is not None:
        path = config.repository.config.format(env=env)
        return miniscule.read_config(path)
    return miniscule.read_config()
