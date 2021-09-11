"""Defines the Bullet class."""
import math
import pyglet
from .vector import Vector2
from .globalvars import BOARD_WIDTH, BOARD_HEIGHT, batch, player_group
from .globaldefs import get_orientation, increment_score

class Bullet:
    """Class for bullets fired by the player."""
    def __init__(self, position, direction):
        """Creates a new Bullet object.

        Args:
            position (Vector2): The starting position of the bullet.
            direction (float): The angle the bullet will travel in radians.
        """
        self.direction = direction
        self.velocity = Vector2(math.cos(direction), math.sin(direction)) * 300
        self.position = position + Vector2(25 * math.cos(direction), 25 * math.sin(direction))
        self.queue_delete = False
        self.shape = pyglet.shapes.Circle(self.position.x, self.position.y, 2, 6, batch=batch, group=player_group)

    def update(self, dt):
        """Updates the bullet position.

        Args:
            dt (float): Time since last update call in seconds.
        """
        self.position += self.velocity * dt
        if self.position.x < 0 or self.position.x > BOARD_WIDTH or self.position.y < 0 or self.position.y > BOARD_HEIGHT:
            self.shape.delete()
            self.queue_delete = True
            return
        self.shape.position = [self.position.x, self.position.y]

    def check_collisions(self, asteroids):
        """Checks for collisions with asteroids.

        Args:
            asteroids (list[Asteroid]): List of all existing Asteroid objects.
        """
        rayPt1 = self.position
        rayPt2 = Vector2(BOARD_WIDTH*2, self.position.y)
        for asteroid in asteroids:
            intersects = 0
            for line_segment in asteroid.line_segments:
                o1 = get_orientation(rayPt1, rayPt2, line_segment[0])
                o2 = get_orientation(rayPt1, rayPt2, line_segment[1])
                o3 = get_orientation(line_segment[0], line_segment[1], rayPt1)
                o4 = get_orientation(line_segment[0], line_segment[1], rayPt2)
                if (o1 != o2 and o3 != o4):
                    intersects += 1
            if intersects % 2 == 1:
                self.queue_delete = True
                asteroid.on_hit(asteroids)
                increment_score()
                return