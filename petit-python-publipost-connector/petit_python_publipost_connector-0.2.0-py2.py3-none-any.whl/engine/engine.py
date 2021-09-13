import io
from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class BytesIO(io.BytesIO):
    @staticmethod
    def of(content: bytes):
        f = io.BytesIO()
        f.write(content)
        return f


class Template(ABC):
    fields: List[str]

    @abstractmethod
    def __init__(self, _file: io.BytesIO):
        ...

    @abstractmethod
    def render(self, data: Dict[str, object], options: Optional[List[str]]) -> io.BytesIO:
        ...
