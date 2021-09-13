import math
from typing import Dict, List, Tuple
import numpy as np
import cooptools.geometry as geo

class IVector:
    def from_ivector(self, ivec):
        raise NotImplementedError()

    def __init__(self, coords: Dict = None):
        if coords is not None:
            self.coords = coords
        else:
            self.coords = {}

    def __getitem__(self, item):
        return self.coords[item]

    def __setitem__(self, key, value):
        self.coords[key] = value

    @classmethod
    def zero_of_degree(cls, other):
        new = IVector()
        for ii, value in other.coords.items():
            new[ii] = 0
        return new

    @property
    def x(self):
        return self.coords.get('x', None)

    @property
    def y(self):
        return self.coords.get('y', None)

    @property
    def z(self):
        return self.coords.get('z', None)

    # THIS DOENST WORK, would like to be able to call via .length or .length(), but havent figured it out yet
    # @property
    # def length(self):
    #     return self.length()

    def degree(self):
        return len(self.coords)

    def unit(self):
        length = self.length()
        if length == 0:
            return None
        new_vector = IVector()
        for coord in self.coords:
            new_vector.coords[coord] = self.coords[coord]/length
        return new_vector

    def length(self):
        sum = 0
        for ii in self.coords:
            sum += self.coords[ii] ** 2

        return math.sqrt(sum)

    def distance_from(self, other):
        if isinstance(other, IVector):
            sum = 0.0
            for ii in self.coords.keys():
                delta = (float(self.coords[ii]) - float(other.coords[ii])) ** 2
                sum += delta
            return math.sqrt(sum)
        else:
            raise TypeError(f"type {other} cannot be distanced from {type(self)}")

    def scaled_to_length(self, desired_length: float):
        new_vector = self.unit()
        if new_vector is None:
            return Vector2(0, 0)

        for ii in new_vector.coords:
            new_vector.coords[ii] = new_vector.coords[ii] * desired_length

        return new_vector


    def __eq__(self, other) -> bool:
        if not (isinstance(other, type(self)) or issubclass(type(other), type(self)) or issubclass(type(self), type(other))):
            return False
        for ii in self.coords.keys():
            if not self._is_close(self.coords[ii], other.coords[ii]):
                return False

        return True

    def __str__(self, n_digits: int = 2):
        ret = "<"
        ii = 0
        for key in self.coords.keys():
            if ii > 0:
                ret += ", "
            ret += f"{round(float(self.coords[key]), n_digits)}"
            ii +=1

        ret +=">"
        return ret

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(str(self))

    def __add__(self, other):
        if not (isinstance(other, type(self)) or issubclass(type(other), type(self)) or issubclass(type(self),
                                                                                                   type(other))):
            raise TypeError(f"Object of type [{type(other)}] cannot be added to {type(self)}")

        ret = IVector()
        for ii in self.coords:
            ret.coords[ii] = self.coords[ii] + other.coords[ii]

        return ret

    def __sub__(self, other):
        if not (isinstance(other, type(self)) or issubclass(type(other), type(self)) or issubclass(type(self), type(other))):
            raise TypeError(f"Object of type [{type(other)}] cannot be subtracted from {type(self)}")

        ret = IVector()
        for ii in self.coords:
            ret.coords[ii] = self.coords[ii] - other.coords[ii]

        return ret

    def __mul__(self, other):
        if not (isinstance(other, float) or isinstance(other, int)):
            raise TypeError(f"Object of type [{type(other)}] cannot be multiplied to {type(self)}")

        new_vector = self.unit()
        if new_vector is None:
            return Vector2(0, 0)

        for ii in new_vector.coords:
            new_vector.coords[ii] = new_vector.coords[ii] * self.length() * other

        return new_vector

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if not (isinstance(other, float) or isinstance(other, int)):
            raise TypeError(f"Object of type [{type(other)}] cannot be divided from {type(self)}")

        new_vector = self.unit()

        if new_vector is None:
            return Vector2(0, 0)

        for ii in new_vector.coords:
            new_vector.coords[ii] = new_vector.coords[ii] * (self.length() / other)

        return new_vector
        # return self.unit() * self.length() / other


    def _is_close(self, a:float, b:float, rel_tol=1e-09, abs_tol=0.0):
        return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

    def dot(self, other):
        if not (isinstance(other, type(self)) or issubclass(type(other), type(self)) or issubclass(type(self), type(other))):
            raise TypeError(f"type {other} cannot be dot multiplied by {type(self)}. Must match type...")

        x = [coord for label, coord in self.coords.items()]
        y = [coord for label, coord in other.coords.items()]

        return np.dot(x, y)

    def cross(self, other):
        if not (isinstance(other, type(self))
                or issubclass(type(other), type(self))
                or issubclass(type(self), type(other))
                or self.degree() != other.degree()):
            raise TypeError(f"type {other} cannot be dot multiplied by {type(self)}. Must match type...")


        x = [coord for label, coord in self.coords.items()]
        y = [coord for label, coord in other.coords.items()]

        cross = np.cross(x, y)

        return IVector({key: cross[ii] for ii, (key, value) in enumerate(self.coords.items())})


    def angle(self, other, origin = None):
        if not (isinstance(other, type(self)) or issubclass(type(other), type(self)) or issubclass(type(self), type(other))):
            raise TypeError(f"type {other} cannot be dot multiplied by {type(self)}. Must match type...")

        if origin is None:
            origin = IVector.zero_of_degree(other)

        a = self - origin
        b = other - origin

        return math.acos((a.dot(b) / (a.length() * b.length())))

    def hadamard_product(self, other):
        if type(other) == float or type(other) == int:
            mult_vec = IVector()
            for coord in self.coords:
                mult_vec.coords[coord] = other
            other = mult_vec

        if not (isinstance(other, type(self)) or issubclass(type(other), type(self)) or issubclass(type(self), type(other))):
            raise TypeError(f"type {other} cannot be hadamard multiplied by {type(self)}. Must match type...")
        else:
            new_vector = IVector()
            for ii in self.coords:
                new_vector.coords[ii] = self.coords[ii] * other.coords[ii]
            return new_vector

    def hadamard_division(self, other, num_digits=None):
        if type(other) == float or type(other) == int:
            div_vec = IVector()
            for coord in self.coords:
                div_vec.coords[coord] = other
            other = div_vec

        if not (isinstance(other, type(self)) or issubclass(type(other), type(self)) or issubclass(type(self), type(other))):
            raise TypeError(f"type {type(other)} cannot be hadamard divided by {type(self)}. Must match type...\n"
                            f"{issubclass(type(other), type(self))}\n"
                            f"{issubclass(type(self), type(other))}")

        else:
            new_vector = IVector()
            for ii in self.coords:
                if num_digits is not None:
                    new_vector.coords[ii] = round(self.coords[ii] * 1.0 / other.coords[ii], num_digits)
                else:
                    new_vector.coords[ii] = self.coords[ii] * 1.0 / other.coords[ii]
            return new_vector

    def bounded_by(self, a, b) -> bool:
        if not isinstance(a, type(self)) and isinstance(b, type(self)):
            raise TypeError(f"a and b must match vector type: {type(self)}. {type(a)} and {type(b)} were given")

        for ii in self.coords.keys():
            min_val = min(a.coords[ii], b.coords[ii])
            max_val = max(a.coords[ii], b.coords[ii])

            if not min_val <= self.coords[ii] <= max_val:
                return False

        return True

    def interpolate(self, other, amount: float = 0.5, interpolate_type: str = "linear" ):
        if not (isinstance(other, type(self)) or issubclass(type(other), type(self)) or issubclass(type(self), type(other))):
            raise TypeError(f"Cannot interpolate between objects of type {type(self)} and {type(other)}")

        if interpolate_type == "linear":
            return (other - self) * amount + self
        else:
            raise NotImplementedError(f"Unimplemented interpolation type: {interpolate_type}")

    def absolute(self):

        abs_coords = {}
        for key, val in self.coords.items():
            abs_coords[key] = abs(val)

        return IVector(abs_coords)

    def project_onto(self, end, start=None):
        if not (isinstance(end, type(self)) or issubclass(type(end), type(self)) or issubclass(type(self),
                                                                                                   type(end))):
            raise TypeError(f"type {end} cannot be projected onto {type(self)}. Must match type...")

        if start is None:
            start = IVector.zero_of_degree(self)

        e1 = end - start
        e2 = self - start

        #https://gamedev.stackexchange.com/questions/72528/how-can-i-project-a-3d-point-onto-a-3d-line
        return start + e2.dot(e1) / e1.dot(e1) * e1

    def closest_within_threshold(self, other_points: List, distance_threshold: float = None):
        if distance_threshold is not None and distance_threshold < 0:
            raise ValueError(f"distance_threshold must be greater than zero, but {distance_threshold} was provided")

        qualifiers = []
        for other in other_points:
            distance = self.distance_from(other)
            if distance_threshold is None or distance < distance_threshold:
                qualifiers.append((other, distance))

        if len(qualifiers) == 0:
            return None

        min_dist = min([x[1] for x in qualifiers])

        return next(iter([x[0] for x in qualifiers if x[1] == min_dist]), None)

    def as_tuple(self):
        return tuple([v for k, v in self.coords.items()])

    def angle_from(self, other=None):
        if other is None:
            other = Vector2(1, 0)

        unit_vector_2 = self.unit().as_tuple()
        unit_vector_1 = other.unit().as_tuple()
        dot_product = np.dot(unit_vector_1, unit_vector_2)
        det = np.linalg.det([unit_vector_1, unit_vector_2])
        angle = math.atan2(-det, -dot_product) + math.pi  # atan2(y, x) or atan2(sin, cos)

        return angle

class Vector2 (IVector):
    @classmethod
    def from_ivector(cls, ivec: IVector):
        return Vector2(ivec.x, ivec.y)

    @classmethod
    def from_vector3(cls, vec3):
        if not type(vec3) == Vector3:
            raise TypeError(f"input type must be {type(Vector3)} but type [{type(vec3)}] was provided")
        return Vector2(vec3.x, vec3.y)

    @classmethod
    def from_tuple(cls, tup: Tuple[float, float]):
        if len(tup) < 2:
            raise ValueError(f"Can only create a Vector2 from a float tuple of size 2 or more. {tup} provided")

        x = float(tup[0])
        y = float(tup[1])

        return Vector2(x, y)

    def __init__(self, x: float, y: float):
        IVector.__init__(self)
        self.coords['x'] = x
        self.coords['y'] = y

    def in_polygon(self, poly: List[IVector]):
        return geo.point_in_polygon(self.as_tuple(), [x.as_tuple()[:2] for x in poly])

class Vector3(IVector):
    @classmethod
    def from_ivector(cls, ivec: IVector):
        return Vector3(ivec.x, ivec.y, ivec.z)

    @classmethod
    def from_vector2(cls, vec2: Vector2, z: float = 0):
        if not type(vec2) == Vector2:
            raise TypeError(f"input type must be {type(Vector2)} but type [{type(vec2)}] was provided")

        return Vector3(vec2.x, vec2.y, z)

    @classmethod
    def from_tuple(cls, tup: Tuple[float, float, float]):
        if len(tup) < 3:
            raise ValueError(f"Can only create a Vector3 from a float tuple of size 3 or more. {tup} provided")

        x = float(tup[0])
        y = float(tup[1])
        z = float(tup[2])

        return Vector3(x, y, z)

    def __init__(self, x: float, y: float, z: float):
        IVector.__init__(self)
        self.coords['x'] = x
        self.coords['y'] = y
        self.coords['z'] = z

if __name__ == "__main__":
    poly = [
        Vector2(2, 2),
        Vector2(3, 3),
        Vector2(2, 3),
        Vector2(3, 2)
    ]

    point = Vector2(2.5, 2.5)

    print(point.in_polygon(poly))

    point = Vector2(1, 1)
    print(point.in_polygon(poly))