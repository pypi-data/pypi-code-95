from dataclasses import dataclass


@dataclass
class Series:
    title: str
    points: list

    def __init__(self, points, title, **rest):
        self.points = points
        self.title = title if title is not None else ''
        if len(rest):
            for key, value in rest.items():
                self.__dict__[key] = value
