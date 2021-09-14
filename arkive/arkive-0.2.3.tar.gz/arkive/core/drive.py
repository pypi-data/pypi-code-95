from pathlib import Path
from abc import ABC, abstractmethod


class Drive(ABC):
    @abstractmethod
    def index(self, folder: Path):
        raise NotImplementedError

    @abstractmethod
    def rename(self, source: Path, dest: Path):
        raise NotImplementedError

    @abstractmethod
    def cleanup(self, folder: Path):
        raise NotImplementedError
