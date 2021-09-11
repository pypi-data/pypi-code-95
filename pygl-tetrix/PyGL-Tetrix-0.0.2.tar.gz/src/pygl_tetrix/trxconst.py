"Defines the batch and groups used in the game."
import pyglet

batch = pyglet.graphics.Batch()
background = pyglet.graphics.OrderedGroup(0)
side_frames = pyglet.graphics.OrderedGroup(1)
foreground = pyglet.graphics.OrderedGroup(2)
labels = pyglet.graphics.OrderedGroup(3)