"""Generates a pyglet window and starts a Tetrix session."""
import pyglet
from .colors import COLORS
from .trxconst import batch, background, side_frames
from .controller import Controller
from .grid import Grid

window = pyglet.window.Window(width=600, height=600, caption="Tetrix")

window_border = batch.add(12, pyglet.gl.GL_QUADS, background,
    ('v2f', (
        0, 0, 0, 600, 120, 600, 120, 0,
        120, 0, 120, 60, 480, 60, 480, 0,
        480, 0, 480, 600, 600, 600, 600, 0
    )),
    ('c3B', COLORS['GRAY'] * 12)
)

hold_frame = batch.add(4, pyglet.gl.GL_QUADS, side_frames,
    ('v2f', (6, 528, 6, 410, 114, 410, 114, 528)),
    ('c3B', COLORS['BLACK'] * 4)
)

next_frame = batch.add(4, pyglet.gl.GL_QUADS, side_frames,
    ('v2f', (594, 528, 594, 410, 486, 410, 486, 528)),
    ('c3B', COLORS['BLACK'] * 4)
)

grid = Grid()
controller = Controller(grid)
grid.register_score_inc(controller.score_inc)

def update(dt):
    controller.drop_timer += dt
    if controller.drop_timer >= controller.auto_drop[controller.level - 1]:
        controller.drop_timer = 0
        controller.piece.move(y=-1)

controller.register_update(update)

@window.event
def on_key_press(symbol, modifiers):
    if not controller.pause:
        if symbol == pyglet.window.key.DOWN:
            controller.piece.move(y=-1)
        elif symbol == pyglet.window.key.LEFT:
            controller.piece.move(x=-1)
        elif symbol == pyglet.window.key.RIGHT:
            controller.piece.move(x=1)
        elif symbol == pyglet.window.key.E:
            controller.piece.rotate()
        elif symbol == pyglet.window.key.Q:
            controller.piece.rotate(cw=False)
    if symbol == pyglet.window.key.SPACE:
        if not controller.game_over:
            if controller.pause:
                pyglet.clock.schedule(update)
            else:
                pyglet.clock.unschedule(update)
            controller.pause = not controller.pause

@window.event
def on_draw():
    window.clear()
    batch.draw()

pyglet.clock.schedule(update)
pyglet.app.run()