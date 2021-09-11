"""Defines the Asteroid class."""
import math
import random
import pyglet
from .vector import Vector2
from .globalvars import BOARD_WIDTH, BOARD_HEIGHT, batch, asteroids_group

class Asteroid:
    def __init__(self, position=None, level=None):
        self.level = level if level is not None else random.randint(1, 3)
        self.radius = random.randrange(self.level * 40 // 2, self.level * 40)
        self.position = position if position is not None else self.generate_rand_pos()
        self.velocity = self.generate_rand_velocity()
        self.queue_delete = False
        self._points = self.generate_rand_points()
        self.shape = batch.add(len(self._points) * 2, pyglet.gl.GL_LINES, asteroids_group,
            ("v2f", self.get_gl_pt_array()),
            ("c3B", [255 for _ in range(3)] * (len(self._points) * 2))
        )

    @property
    def points(self):
        return [pt + self.position for pt in self._points]

    @property
    def line_segments(self):
        ls = []
        pts = self.points
        for i in range(len(pts)):
            p1 = pts[i]
            p2 = pts[0] if i + 1 == len(pts) else pts[i+1]
            ls.append([p1, p2])
        return ls

    def get_gl_pt_array(self):
        gl_pts = []
        for i in range(len(self.points)):
            pt1 = self.points[i]
            pt2 = self.points[0] if i + 1 == len(self.points) else self.points[i+1]
            gl_pts.extend([pt1.x, pt1.y, pt2.x, pt2.y])
        return gl_pts

    def on_hit(self, asteroids):
        self.level -= 1
        if self.level > 0:
            asteroids.append(Asteroid(self.position, self.level))
            asteroids.append(Asteroid(self.position, self.level))
        self.queue_delete = True
        self.shape.delete()

    def generate_rand_pos(self):
        pos_factor = random.randrange(0, BOARD_WIDTH * 2 + BOARD_HEIGHT * 2)
        if pos_factor < BOARD_WIDTH:
            return Vector2(pos_factor, -self.radius)
        if pos_factor < BOARD_WIDTH + BOARD_HEIGHT:
            return Vector2(BOARD_WIDTH + self.radius, pos_factor - BOARD_WIDTH)
        if pos_factor < BOARD_WIDTH * 2 + BOARD_HEIGHT:
            return Vector2(pos_factor - (BOARD_WIDTH + BOARD_HEIGHT), BOARD_HEIGHT + self.radius)
        return Vector2(-self.radius, pos_factor - (BOARD_WIDTH * 2 + BOARD_HEIGHT))

    def generate_rand_velocity(self):
        speed = random.randrange((4 - self.level) * 40 // 2, (4 - self.level) * 40)
        angle_to_center = (Vector2(BOARD_WIDTH/2, BOARD_HEIGHT/2) - self.position).angle
        if self.position.x > 0 and self.position.x < BOARD_WIDTH and self.position.y > 0 and self.position.y < BOARD_HEIGHT:
            angle = angle_to_center + random.uniform(-math.pi, math.pi)
        else:
            angle = angle_to_center + random.uniform(-math.pi/4, math.pi/4)
        return Vector2(speed * math.cos(angle), speed * math.sin(angle))

    def generate_rand_points(self):
        pts = []
        start_angle = random.uniform(-math.pi/4, math.pi/4)
        angle = 0
        while angle < 2 * math.pi:
            rad = random.randrange(self.radius//2, self.radius)
            pts.append(Vector2(rad * math.cos(angle + start_angle), rad * math.sin(angle + start_angle)))
            angle += random.uniform(math.pi/4, 3*math.pi/4)
        return pts

    def update(self, dt):
        self.position += self.velocity * dt
        if (self.position.x < -self.radius
            or self.position.x > BOARD_WIDTH + self.radius
            or self.position.y < -self.radius
            or self.position.y > BOARD_HEIGHT + self.radius):
            self.shape.delete()
            self.queue_delete = True
        self.shape.vertices = self.get_gl_pt_array()