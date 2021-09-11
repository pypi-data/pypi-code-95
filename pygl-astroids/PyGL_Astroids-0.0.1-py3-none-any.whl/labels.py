"""Defines the labels used in the game."""
import pyglet
from .globalvars import BOARD_HEIGHT, batch, label_group

score_label = pyglet.text.Label(text="Score: 0", x=10, y=BOARD_HEIGHT-10, anchor_y="top", batch=batch, group=label_group)
gameover_label = None