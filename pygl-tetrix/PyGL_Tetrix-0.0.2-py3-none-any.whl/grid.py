"""Defines the Grid class which manages the other componenets."""
class Grid:
    """Grid class for managing game objects"""
    def __init__(self):
        """Creates a new Grid object.

        Args:
            controller (Controller): The game controller instance.
        """
        self.tiles = [[None for _ in range(10)] for _ in range(15)]

    def register_score_inc(self, score_inc):
        """Registers a function to increment the score."""
        self.score_inc = score_inc

    def add(self, square, x=0, y=0):
        """Adds a square to the grid at the specified position.

        Args:
            square (Square): The square to add to the grid.
            x (int, optional): The x position of the Square. Defaults to 0.
            y (int, optional): The y position of the Square. Defaults to 0.
        """
        self.tiles[y][x] = square

    def remove_row(self, row):
        """Removes all Squares in the specified row from the grid.

        Args:
            row (int): The row index to remove Square objects from.
        """
        for square in self.tiles[row]:
            square.shape.delete()
        self.tiles[row].clear()
        self.tiles[row] = [None for _ in range(10)]
        for i in range(row + 1, len(self.tiles)):
            for j in range(10):
                if self.tiles[i][j] is not None:
                    self.tiles[i][j].move(y=-1)
                    square = self.tiles[i][j]
                    self.tiles[i][j] = None
                    self.tiles[i - 1][j] = square

    def check(self):
        """Checkes each row to determine if it is complete."""
        while True:
            rows_cleared = False
            for i in range(len(self.tiles)):
                if all(self.tiles[i]):
                    self.remove_row(i)
                    self.score_inc()
                    rows_cleared = True
            if not rows_cleared:
                break