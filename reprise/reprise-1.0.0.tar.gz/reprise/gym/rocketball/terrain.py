
class Terrain(object):

    def __init__(self, start, end, color, gravity, noise):
        self.start = start
        self.end = end
        self.color = color
        self.gravity = gravity
        self.noise = noise

    def contains(self, position):
        return (self.start <= position).all() and (position <= self.end).all()
