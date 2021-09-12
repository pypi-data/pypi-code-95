abc = 'ABCDEFGHIJKLMNSOPQRSTUVWXYZ'


class CellPosition:
    def __init__(self, x: int, y: int, position: str = None):
        self.x = x
        self.y = y + 1
        self.position = self.position()
        # self.position = str(chr(self.x)) + str(self.y)

    def position(self):
        return abc[self.x] + str(self.y)
    