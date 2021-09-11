"""Defines the various pyglet labels to be used in the game."""
import pyglet
from .trxconst import batch, labels

level_label = pyglet.text.Label(
    'Level 1',
    font_size=20,
    x=540, y=370,
    anchor_x='center',
    batch=batch,
    group=labels
)
score_label = pyglet.text.Label(
    'Score: 0',
    font_size=16,
    x=540, y=330,
    anchor_x='center',
    batch=batch,
    group=labels
)