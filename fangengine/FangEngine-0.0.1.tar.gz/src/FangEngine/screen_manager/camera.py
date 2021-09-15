import typing


class Camera:
    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y

    def get_pos(self) -> typing.Tuple[float, float]:
        return self.x, self.y
