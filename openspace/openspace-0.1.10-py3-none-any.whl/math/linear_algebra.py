import numpy as np
from math import acos, cos, sin

def get_first_axis_rotation_matrix(ang):
    return Matrix([
        [1, 0, 0],
        [0, cos(ang), sin(ang)],
        [0, -sin(ang), cos(ang)]
    ])

def get_second_axis_rotation_matrix(ang):
    return Matrix([
        [cos(ang), 0, -sin(ang)],
        [0, 1, 0],
        [sin(ang), 0, cos(ang)]
    ])

def get_third_axis_rotation_matrix(ang):
    return Matrix([
        [cos(ang), sin(ang), 0],
        [-sin(ang), cos(ang), 0],
        [0, 0, 1]
    ])

class Matrix(np.ndarray):

    def __new__(cls, elements):
        
        self = np.asarray(elements).view(cls)
            
        self.dimension = self.shape
        self.rows = self.dimension[0]
        self.columns = self.dimension[1]

        return self

    def multiply(self, array):

        if self.columns == array.rows:
            if (array.columns == 1):
                result = Vector(np.dot(self, array)) 
            else:
                result = Matrix(np.dot(self, array)) 

            return result

    def get_transpose(self):
        return Matrix(self.T)

    def get_inverse(self):
        return Matrix(np.linalg.inv(self))
        
class Vector(np.ndarray):

    def __new__(cls, elements):
        
        if type(elements) == list:
            self = np.asarray(elements).reshape(len(elements), 1).view(cls)
        else:
            self = np.asarray(elements).view(cls)
            
        self.dimension = self.shape
        self.rows = self.dimension[0]
        self.columns = self.dimension[1]

        return self

    def plus(self, vector_to_add):
        if self.dimension == vector_to_add.dimension:
            return Vector(self + vector_to_add)

    def minus(self, vector_to_subtract):
        if self.dimension == vector_to_subtract.dimension:
            return Vector(self - vector_to_subtract)

    def distance(self, position):
        if self.dimension == position.dimension:
            return self.minus(position).magnitude()

    def magnitude(self):
        return np.linalg.norm(self)

    def dot(self, vector):
        if self.dimension == vector.dimension:
            return np.dot(self.reshape(1, self.rows), vector)[0][0]

    def normalized(self):
        return Vector(self/np.linalg.norm(self))

    def angle(self, vector):
        if self.dimension == vector.dimension:
            return acos(self.dot(vector)/(self.magnitude()*vector.magnitude()))

    def cross(self, vector):
        if self.dimension == vector.dimension:
            return Vector(np.cross(self, vector, axis=0))

    def rotate_about_x(self, ang):
        m = get_first_axis_rotation_matrix(ang)
        
        return m.multiply(self)

    def rotate_about_y(self, ang):
        m = get_second_axis_rotation_matrix(ang)

        return m.multiply(self)

    def rotate_about_z(self, ang):
        m = get_third_axis_rotation_matrix(ang)

        return m.multiply(self)

    def get_element(self, element):
        return self[element][0]

    def scale(self, multiple):
        return Vector(self*multiple)

        