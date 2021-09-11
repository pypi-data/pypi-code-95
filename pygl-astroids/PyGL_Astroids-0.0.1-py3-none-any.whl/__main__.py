import random
import pyglet
from pyglet.window import key
from .globalvars import board, AST_GEN_FREQ, batch
from .globaldefs import reset_score
from .labels import gameover_label
from .player import Player
from .asteroid import Asteroid
from .bullet import Bullet

player = Player()
asteroids = []
bullets = []

def update(dt):
    """Called by pyglet each to update the board during each frame.

    Args:
        dt (float): Time since last update call in seconds.
    """
    # Update object positions
    player.update(dt)
    if random.random() < AST_GEN_FREQ * dt:
        asteroids.append(Asteroid())
    for bullet in bullets:
        bullet.update(dt)
    for asteroid in asteroids:
        asteroid.update(dt)
    # Check for collisions
    if player.state == "live":
        player.check_collisions(asteroids)
    for bullet in bullets:
        bullet.check_collisions(asteroids)
    # Free unnecessary objects
    bullets[:] = [bullet for bullet in bullets if not bullet.queue_delete]
    asteroids[:] = [asteroid for asteroid in asteroids if not asteroid.queue_delete]

@board.event
def on_key_press(symbol, modifiers):
    if symbol in [key.UP, key.LEFT, key.DOWN, key.RIGHT]:
        if not symbol in player.inputs:
            player.inputs.append(symbol)
    if symbol == key.SPACE:
        if player.state == "live":
            bullets.append(Bullet(player.position, player.angle))
        elif player.state == "dead":
            gameover_label.delete()
            reset_score()
            for asteroid in asteroids:
                asteroid.shape.delete()
            asteroids.clear()
            player.reset()
            

@board.event
def on_key_release(symbol, modifiers):  
    if symbol in [key.UP, key.LEFT, key.DOWN, key.RIGHT]:
        while symbol in player.inputs:
            player.inputs.remove(symbol)

@board.event
def on_draw():
    board.clear()
    batch.draw()

pyglet.clock.schedule(update)
pyglet.app.run()