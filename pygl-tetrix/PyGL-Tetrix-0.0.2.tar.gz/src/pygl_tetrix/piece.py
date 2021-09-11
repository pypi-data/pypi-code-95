"""Defines the Piece class wihch controls its Square objects."""
import random
import math
from .square import Square
from .ptypes import PTYPES

class Piece():
    """Piece object which manages a set of Square objects."""
    def __init__(self, controller, grid):
        """Creates a new Piece object.

        Args:
            controller (Controller): A board controller object.
            grid (Grid): A Grid object.
        """
        self.controller = controller
        self.grid = grid
        self.type = random.choice(['I', 'J', 'L', 'O', 'S', 'T', 'Z'])
        color = random.choice(['BLUE', 'CYAN', 'GREEN', 'MAGENTA', 'RED', 'YELLOW'])
        self.color = color
        self.squares = [Square(grid, [square[0], square[1]], self.color) for square in PTYPES[self.type]['squares']]
        self.rotate_pt = list(PTYPES[self.type]['rotate_pt'])
        self.next = True
        self.hold = False

    def move(self, x=0, y=0):
        """Moves the Piece by the specified amount in the x and y directions.

        Args:
            x (int, optional): The movement of the Piece in the x direction. Defaults to 0.
            y (int, optional): The movement of the Piece in the y direction. Defaults to 0.
        """
        if all([square.move_check(x, y) for square in self.squares]):
            for square in self.squares:
                square.move(x, y)
            if self.rotate_pt is not None:
                self.rotate_pt[0] += x
                self.rotate_pt[1] += y
            self.controller.drop_timer = 0
        elif y == -1:
            for square in self.squares:
                self.grid.add(square, square.position[0], square.position[1])
            self.squares.clear()
            self.grid.check()
            self.controller.get_next_piece()

    def rotate(self, cw=True):
        """Rotates the Piece in the specified direction.

        Args:
            cw (bool, optional): The rotation direction where True is clockwise and False is counter-clockwise. Defaults to True.
        """
        move_checks = []
        moves = []
        for square in self.squares:
            x = square.position[0] - self.rotate_pt[0]
            y = square.position[1] - self.rotate_pt[1]
            angle = math.atan2(y, x)
            if cw:
                angle -= math.pi / 2
            else:
                angle += math.pi / 2
            rad = math.sqrt((x * x) + (y * y))
            new_pos = [rad * math.cos(angle), rad * math.sin(angle)]
            new_move = [new_pos[0] - x, new_pos[1] - y]
            moves.append(new_move)
            move_checks.append(square.move_check(new_move[0], new_move[1]))
        if all(move_checks):
            for i in range(len(self.squares)):
                self.squares[i].move(moves[i][0], moves[i][1])