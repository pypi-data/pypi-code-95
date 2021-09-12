# -*- coding:utf-8  -*-

from turtle import *

class Draw():
    def __init__(self, pen_attribute=None):
        if pen_attribute == None:
            self.pen = Pen()
        else:
            self.pen = pen_attribute
    def create_triangle(self, distance, angle=90, fill=None):
        self.pen.setheading(angle)
        # Angle
        if fill != None:
            self.pen.fillcolor(fill)
            self.pen.begin_fill()
        self.pen.left(30)
        for x in range(0, 3):
            self.pen.right(120)
            self.pen.forward(distance)
        self.pen.left(30)
        if fill != None:
            self.pen.end_fill()
        # Draw
    def create_rectangle(self, distance_x, distance_y, angle=90, fill=None):
        self.pen.setheading(angle)
        # Angle
        if fill != None:
            self.pen.fillcolor(fill)
            self.pen.begin_fill()
        for x in range(0, 2):
            self.pen.forward(distance_x)
            self.pen.right(90)
            self.pen.forward(distance_y)
            self.pen.right(90)
        if fill != None:
            self.pen.end_fill()
        # Draw
    def create_pentagon(self, distance, angle=90, fill=None):
        self.pen.setheading(angle)
        # Angle
        if fill != None:
            self.pen.fillcolor(fill)
            self.pen.begin_fill()
        for x in range(0, 5):
            self.pen.forward(distance)
            self.pen.right(72)
        if fill != None:
            self.pen.end_fill()
        # Draw
    def create_polygon(self, side, distance, angle=90, fill=None):
        internal_angle_sum = (side - 2) * 180
        # Value
        self.pen.setheading(angle)
        # Angle
        if fill != None:
            self.pen.fillcolor(fill)
            self.pen.begin_fill()
        for x in range(0, side):
            self.pen.forward(distance)
            self.pen.right(180 - internal_angle_sum / side)
        if fill != None:
            self.pen.end_fill()
        # Draw
    def create_pg(self, side, thickness, size=1, angle=90, fill=None) -> 'create psychedelic graphics':
        internal_angle_sum = (side - 2) * 180
        # Value
        self.pen.setheading(angle)
        # Angle
        pencolor = self.pen.pencolor()
        if fill != None:
            self.pen.pencolor(fill)
        for x in range(thickness * side):
            self.pen.forward(x * size)
            self.pen.right(180 - internal_angle_sum / side)
        self.pen.pencolor(pencolor)
        # Draw
    def create_pg1(self, side, thickness, size=1, rotation=1, angle=90, fill=None) -> '''create psychedelic graphics 1
The fewer sides, the more effective''':
        internal_angle_sum = (side - 2) * 180
        # Value
        self.pen.setheading(angle)
        # Angle
        pencolor = self.pen.pencolor()
        if fill != None:
            self.pen.pencolor(fill)
        for x in range(thickness * side):
            self.pen.forward(x * size)
            self.pen.right((180 - internal_angle_sum / side) + rotation)
        self.pen.pencolor(pencolor)
        # Draw
    def create_koch(self, order, size=1, angle=90, fill=None) -> 'koch curve':
        self.pen.setheading(angle)
        # Angle
        pencolor = self.pen.pencolor()
        if fill != None:
            self.pen.pencolor(fill)
        if order == 0:
            self.pen.forward(size)
        else:
            self.create_koch_curve(order - 1, size=size)
            self.pen.left(60)
            self.create_koch_curve(order - 1, size=size)
            self.pen.right(120)
            self.create_koch_curve(order - 1, size=size)
            self.pen.left(60)
            self.create_koch_curve(order - 1, size=size)
        self.pen.pencolor(pencolor)
        # Draw
    def create_koch_curve(self, order, size) -> 'koch curve service':
        if order == 0:
            self.pen.forward(size)
        else:
            self.create_koch_curve(order - 1, size=size)
            self.pen.left(60)
            self.create_koch_curve(order - 1, size=size)
            self.pen.right(120)
            self.create_koch_curve(order - 1, size=size)
            self.pen.left(60)
            self.create_koch_curve(order - 1, size=size)
    def create_koch_snowflake(self, order, size=1, angle=90, fill=None) -> 'koch snowflake':
        pencolor = self.pen.pencolor()
        if fill != None:
            self.pen.pencolor(fill)
        for x in range(3):
            self.create_koch(order, size, angle, fill)
            self.pen.right(120)
        self.pen.pencolor(pencolor)
