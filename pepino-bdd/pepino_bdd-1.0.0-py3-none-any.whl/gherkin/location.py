import abc


class GherkinLocation(abc.ABC):
    def __init__(self, parsed):
        self.line: int = parsed["location"]["line"]
        self.cursor: int = parsed["location"]["column"]

    @property
    def position(self):
        return f"{self.line}:{self.cursor}"
