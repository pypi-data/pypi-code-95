"""Defines the labels used in the game."""
import pyglet
from .globalvars import BOARD_WIDTH, BOARD_HEIGHT, batch, label_group, gameover_group

score_label = pyglet.text.Label(text="Score: 0", x=10, y=BOARD_HEIGHT-10, anchor_y="top", batch=batch, group=label_group)
gameover_label = pyglet.text.Label(
                    "GAME OVER\nPress 'space' to restart.",
                    font_size=20,
                    x=BOARD_WIDTH//2, y = BOARD_HEIGHT//2,
                    width=BOARD_WIDTH,
                    anchor_x="center", anchor_y="center",
                    align="center",
                    multiline=True,
                    batch=batch,
                    group=gameover_group
                )