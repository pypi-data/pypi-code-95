"""Defines the Player class."""
import math
import pyglet
from pyglet.window import key
from .globalvars import BOARD_WIDTH, BOARD_HEIGHT, batch, player_group, label_group
from .globaldefs import get_orientation
from .vector import Vector2

class Player:
    """Class which manages and controls player inputs, position, state, etc."""
    def __init__(self):
        """Creates a new Player object."""
        self.position = Vector2(BOARD_WIDTH/2, BOARD_HEIGHT/2)
        self.velocity = Vector2()
        self.angle = 0
        self.max_speed = 150
        self.acceleration = 100
        self.rotate_speed = math.pi
        self.state = "live"
        self.explode_time = 0
        self.inputs = []
        pts = self.points
        self.shape = batch.add(8, pyglet.gl.GL_LINES, player_group,
            ("v2f", (
                pts[0].x, pts[0].y, pts[1].x, pts[1].y,
                pts[1].x, pts[1].y, pts[2].x, pts[2].y,
                pts[2].x, pts[2].y, pts[3].x, pts[3].y,
                pts[3].x, pts[3].y, pts[0].x, pts[0].y
            )),
            ("c3B", [255 for _ in range(3)] * 8)
        )

    @property
    def points(self):
        return [
            Vector2(math.cos(self.angle), math.sin(self.angle)) * 25 + self.position,
            Vector2(math.cos(self.angle + 3*math.pi/4), math.sin(self.angle + 3*math.pi/4)) * 25 + self.position,
            Vector2(math.cos(self.angle + math.pi), math.sin(self.angle + math.pi)) * 10 + self.position,
            Vector2(math.cos(self.angle - 3*math.pi/4), math.sin(self.angle - 3*math.pi/4)) * 25 + self.position
        ]

    @property
    def line_segments(self):
        ls = []
        pts = self.points
        for i in range(len(pts)):
            p1 = pts[i]
            p2 = pts[0] if i + 1 == len(pts) else pts[i+1]
            ls.append([p1, p2])
        return ls

    def update(self, dt):
        """Updates the player positions and state.

        Args:
            dt (float): Time since last update call in seconds.
        """
        if self.state == "live":
            unit_vec = Vector2()
            if key.UP in self.inputs:
                unit_vec += Vector2(math.cos(self.angle), math.sin(self.angle))
            if key.DOWN in self.inputs:
                unit_vec -= Vector2(math.cos(self.angle), math.sin(self.angle))
            accel = unit_vec * self.acceleration * dt
            self.velocity += accel
            if not (key.UP in self.inputs or key.DOWN in self.inputs):
                self.velocity -= self.velocity/2 * dt
            if self.velocity.magnitude > self.max_speed:
                self.velocity = self.velocity.normalized() * self.max_speed
            self.position += self.velocity * dt
            while self.position.x < 0:
                self.position.x += BOARD_WIDTH
            while self.position.x > BOARD_WIDTH:
                self.position.x -= BOARD_WIDTH
            while self.position.y < 0:
                self.position.y += BOARD_HEIGHT
            while self.position.y > BOARD_HEIGHT:
                self.position.y -= BOARD_HEIGHT
            rotation = 0
            if key.LEFT in self.inputs:
                rotation += 1
            if key.RIGHT in self.inputs:
                rotation -= 1
            self.angle += rotation * self.rotate_speed * dt
            pts = self.points
            self.shape.vertices = [
                pts[0].x, pts[0].y, pts[1].x, pts[1].y,
                pts[1].x, pts[1].y, pts[2].x, pts[2].y,
                pts[2].x, pts[2].y, pts[3].x, pts[3].y,
                pts[3].x, pts[3].y, pts[0].x, pts[0].y
            ]
        elif self.state == "explode":
            self.explode_time += dt
            dist = 20 * self.explode_time/2 + 5
            if self.explode_time < 2:
                radius = 2 * math.sin(2 * math.pi * 1.125 * self.explode_time) + 4
            elif self.explode_time < 3:
                radius = 3 * math.cos(math.pi * self.explode_time) + 3
            else:
                for particle in self.particles:
                    particle.delete()
                self.particles = []
                self.state = "dead"
                global gameover_label
                gameover_label = pyglet.text.Label(
                    "GAME OVER\nPress 'space' to restart.",
                    font_size=20,
                    x=BOARD_WIDTH//2, y = BOARD_HEIGHT//2,
                    width=BOARD_WIDTH,
                    anchor_x="center", anchor_y="center",
                    align="center",
                    multiline=True,
                    batch=batch,
                    group=label_group
                )
                return
            for i in range(len(self.particles)):
                x = dist * math.cos((i/2) * math.pi + math.pi/4)
                y = dist * math.sin((i/2) * math.pi + math.pi/4)
                self.particles[i].position = [x + self.position.x, y + self.position.y]
                self.particles[i].radius = radius

    def reset(self):
        """Resets the player position, angle, and state."""
        self.position = Vector2(BOARD_WIDTH/2, BOARD_HEIGHT/2)
        self.velocity = Vector2()
        self.angle = 0
        self.state = "live"
        self.explode_time = 0
        pts = self.points
        self.shape = batch.add(8, pyglet.gl.GL_LINES, player_group,
            ("v2f", (
                pts[0].x, pts[0].y, pts[1].x, pts[1].y,
                pts[1].x, pts[1].y, pts[2].x, pts[2].y,
                pts[2].x, pts[2].y, pts[3].x, pts[3].y,
                pts[3].x, pts[3].y, pts[0].x, pts[0].y
            )),
            ("c3B", [255 for _ in range(3)] * 8)
        )

    def process_collision(self):
        """Changes the player state and display after collision."""
        self.state = "explode"
        self.shape.delete()
        self.particles = [pyglet.shapes.Circle(0, 0, 0, 10, batch=batch, group=player_group) for _ in range(4)]

    def check_collisions(self, asteroids):
        """Checks for collisions with asteroids.

        Args:
            asteroids (list[Asteroid]): List of all existing Asteroid objects.
        """
        for segment in self.line_segments:
            shipPt1 = segment[0]
            shipPt2 = segment[1]
            for asteroid in asteroids:
                for line_seg in asteroid.line_segments:
                    o1 = get_orientation(shipPt1, shipPt2, line_seg[0])
                    o2 = get_orientation(shipPt1, shipPt2, line_seg[1])
                    o3 = get_orientation(line_seg[0], line_seg[1], shipPt1)
                    o4 = get_orientation(line_seg[0], line_seg[1], shipPt2)
                    if o1 != o2 and o3 != o4:
                        self.process_collision()
                        return