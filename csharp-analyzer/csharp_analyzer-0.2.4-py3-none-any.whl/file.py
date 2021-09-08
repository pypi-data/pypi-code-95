from .namespace import Namespace
from dataclasses import dataclass
import re


@dataclass
class File:
    Name: str = ''
    Path: str = ''
    Code: str = ''
    Namespace_: Namespace = Namespace()

    def create_tree(self):
        namespace_match = re.search(
            r"namespace\s*([a-zA-Z\.]*)\s*\{\s*([\s\S]*)\s*}", self.Code)
        if namespace_match is None:
            return self
        self.Namespace_ = Namespace(
            Name=namespace_match.group(1),
            Code=namespace_match.group(2)[:-1]).create_tree()
        return self
