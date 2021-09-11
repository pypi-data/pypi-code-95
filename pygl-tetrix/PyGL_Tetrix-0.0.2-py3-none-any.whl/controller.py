"""Defines the game controller object."""
import pyglet
from .piece import Piece
from .labels import *
from .trxconst import batch, labels

class Controller:
    """Contoller object which manages the various game components."""
    def __init__(self, grid):
        """Creates a new Controller object.

        Args:
            grid (Grid): A Grid object for tracking game components.
        """
        self.grid = grid
        self.get_next_piece()
        self.held = None
        self.pause = False
        self.level = 1
        self.drop_timer = 0
        self.score = 0
        self.auto_drop = [2, 1.5, 1.25, 1, 0.75, 0.5, 0.4, 0.3]
        self.game_over = False

    def register_update(self, update):
        """Sets a function as the controller's update function.

        Args:
            update (function): A function which is called for each frame.
        """
        self.update = update

    def score_inc(self):
        """Increments the game score and updates the labels."""
        self.score += 1
        score_label.text = f'Score: {self.score}'
        if self.score == (5 * self.level) and self.level < 8:
            self.level += 1
            level_label.text = f'Level {self.level}'

    def get_next_piece(self):
        """Generates a new piece and checks for game over conditions."""
        self.piece = Piece(self, self.grid)
        for square in self.piece.squares:
            if self.grid.tiles[square.position[1]][square.position[0]] is not None:
                self.pause = True
                self.game_over = True
                batch.add(4, pyglet.gl.GL_QUADS, labels,
                    ('v2f', (138, 252, 138, 360, 462, 360, 462, 252)),
                    ('c3B', [64, 64, 64] * 4)
                )
                pyglet.text.Label(
                    'GAME\nOVER',
                    font_size=36,
                    x=300, y=294,
                    anchor_x='center',
                    batch=batch,
                    group=labels
                )
                pyglet.clock.unschedule(self.update)
                break