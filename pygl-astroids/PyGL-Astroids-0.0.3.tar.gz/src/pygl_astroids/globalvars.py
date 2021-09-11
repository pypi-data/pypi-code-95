"""Defines global variables."""
import pyglet

BOARD_WIDTH = 640
BOARD_HEIGHT = 448
AST_GEN_FREQ = 1/2  # Number of asteroids generated / time in seconds

board = pyglet.window.Window(BOARD_WIDTH, BOARD_HEIGHT, caption="PyGL-Astroids")
batch = pyglet.graphics.Batch()
asteroids_group = pyglet.graphics.OrderedGroup(0)
player_group = pyglet.graphics.OrderedGroup(1)
label_group = pyglet.graphics.OrderedGroup(2)
gameover_group = pyglet.graphics.OrderedGroup(3)
gameover_group.visible = False