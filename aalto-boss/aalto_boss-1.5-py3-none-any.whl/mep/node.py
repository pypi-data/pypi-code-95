import numpy as np


class Node:
    def __init__(self, coords, parent, name=None):
        self.coords = coords
        self.children = []
        self.parent = parent
        if name != None:
            self.name = name
        else:
            self.name = parent.name

    def get_closest_point(self, point, space):
        closest = self
        smallest_dist = np.linalg.norm(space.vec(self.coords, point))
        for child in self.children:
            close, dist = child.get_closest_point(point, space)
            if dist < smallest_dist:
                closest = close
                smallest_dist = dist
        return (closest, smallest_dist)

    def get_all_children(self):
        all_children = [self]
        for child in self.children:
            all_children.extend(child.get_all_children())
        return all_children

    def get_all_parents(self):
        if self.parent == None:
            return []
        else:
            parents = [self.parent]
            parents.extend(self.parent.get_all_parents())
            return parents

    def get_random_child(self):
        all_children = self.get_all_children()
        return np.random.choice(all_children, size=1)[0]
