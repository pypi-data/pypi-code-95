"""Defines the Square class for tetrix pieces."""
import pyglet
import random
from .colors import COLORS
from .trxconst import batch, foreground

class Square():
    """Square class for individual parts of tetrix pieces."""
    def __init__(self, grid, position=[0, 0], color=None):
        """Creates a new Square object.

        Args:
            batch (Batch): The batch that the pyglet data will be added to.
            group (Group): The ordered group to which the pyglet data belongs.
            grid (Grid): The Grid object which manages the object.
            position (list, optional): The position of the square in the form [x, y]. Defaults to [0, 0].
            color (str, optional): The color of the Square as a str. Defaults to None.
        """
        self.position = position
        self.grid = grid
        if color is not None:
            self.color = color
        else:
            self.color = random.choice(['BLUE', 'CYAN', 'GREEN', 'MAGENTA', 'RED', 'YELLOW'])
        x, y = [position[0] * 36 + 120, position[1] * 36 + 60]
        self.shape = batch.add(20, pyglet.gl.GL_QUADS, foreground,
            ('v2f', (
                x, y, x + 6, y + 6, x + 6, y + 30, x, y + 36,
                x, y + 36, x + 6, y + 30, x + 30, y + 30, x + 36, y + 36,
                x + 36, y + 36, x + 30, y + 30, x + 30, y + 6, x + 36, y,
                x + 36, y, x + 30, y + 6, x + 6, y + 6, x, y,
                x + 6, y + 6, x + 6, y + 30, x + 30, y + 30, x + 30, y + 6
            )),
            ('c3B', (
                (COLORS[self.color]['dark'] * 8)
                + (COLORS[self.color]['light'] * 8)
                + (COLORS[self.color]['med'] * 4)
            ))
        )

    def move(self, x=0, y=0):
        """Moves the square by the specified x and y units.

        Args:
            x (int, optional): The movement of the Square in the x direction. Defaults to 0.
            y (int, optional): The movement of the Square in the y direction. Defaults to 0.
        """
        self.position[0] = round(self.position[0] + x)
        self.position[1] = round(self.position[1] + y)
        xpos, ypos = [self.position[0] * 36 + 120, self.position[1] * 36 + 60]
        self.shape.vertices = [
            xpos, ypos, xpos + 6, ypos + 6, xpos + 6, ypos + 30, xpos, ypos + 36,
            xpos, ypos + 36, xpos + 6, ypos + 30, xpos + 30, ypos + 30, xpos + 36, ypos + 36,
            xpos + 36, ypos + 36, xpos + 30, ypos + 30, xpos + 30, ypos + 6, xpos + 36, ypos,
            xpos + 36, ypos, xpos + 30, ypos + 6, xpos + 6, ypos + 6, xpos, ypos,
            xpos + 6, ypos + 6, xpos + 6, ypos + 30, xpos + 30, ypos + 30, xpos + 30, ypos + 6
        ]

    def move_check(self, x=0, y=0):
        """Checks whether the tile to which the Square will move is empty.

        Args:
            x (int, optional): The movement of the Square in the x direction. Defaults to 0.
            y (int, optional): The movement of the Square in the y direction. Defaults to 0.

        Returns:
            bool: True if no other Square is occupying the target tile and False otherwise
        """
        xpos, ypos = self.position
        newx = round(xpos + x)
        newy = round(ypos + y)
        if 0 <= newx < 10 and 0 <= newy < 15:
            if self.grid.tiles[newy][newx] is None:
                return True
            else:
                return False
        else:
            return False