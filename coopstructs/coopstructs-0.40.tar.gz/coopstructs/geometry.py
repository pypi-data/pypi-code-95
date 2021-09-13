from coopstructs.vectors import Vector2
import math
from typing import List, Tuple
import cooptools.geometry as geo
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon
from cooptools.geometry import collinear_points


class Rectangle:
    def __init__(self, x, y, height, width):
        self.x = x
        self.y = y
        self.height = height
        self.width = width

    def points_tuple(self):
        return ((self.x, self.y), (self.x + self.width, self.y), (self.x + self.width, self.y + self.height),
                (self.x, self.y + self.height))

    @property
    def center(self) -> Vector2:
        return Vector2(self.x + self.width / 2, self.y + self.height / 2)

    def __str__(self):
        return f"TopLeft: <{self.x}, {self.y}>, Size: H{self.height} x W{self.width}"


class Line:
    def __init__(self, origin: Vector2, destination: Vector2):

        if origin == destination:
            raise ValueError(f"origin and destination cannot be equal: {origin}")

        self.origin = origin
        self.destination = destination
        # self.length = self.length()

    @property
    def length(self):
        try:
            return (self.destination - self.origin).length()
        except Exception as e:
            print(f"Destination: {self.destination}\n"
                  f"Origin: {self.origin}\n"
                  f"{e}")
            raise

    def intersection(self, other_line) -> Vector2:
        if not type(other_line) == Line:
            raise TypeError(f"can only intersect with objects of type <Line> but type {type(other_line)} was provided")

        xdiff = (self.origin.x - self.destination.x, other_line.origin.x - other_line.destination.x)
        ydiff = (self.origin.y - self.destination.y, other_line.origin.y - other_line.destination.y)

        # handle meet at ends case:
        if self.origin in [other_line.origin, other_line.destination]:
            return self.origin
        elif self.destination in [other_line.origin, other_line.destination]:
            return self.destination

        # handle collinear lines
        if collinear_points([self.origin.as_tuple(), self.destination.as_tuple(), other_line.origin.as_tuple(),
                             other_line.destination.as_tuple()]):
            raise Exception("Lines are collinear")

        def det(a, b):
            return a[0] * b[1] - a[1] * b[0]

        div = det(xdiff, ydiff)
        if div == 0:
            raise Exception('lines do not intersect')

        d = (det(self.origin.as_tuple(), self.destination.as_tuple()),
             det(other_line.origin.as_tuple(), other_line.destination.as_tuple())
             )
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div
        return Vector2(x, y)


class Circle:

    @classmethod
    def from_boundary_points(cls, point1: Vector2, point2: Vector2, point3: Vector2):
        lst = [point1, point2, point3]
        if not len(lst) == len(set(lst)):
            raise ValueError(
                f"All the points must be different for a circle to be created. {point1}, {point2}, {point3} were provided")

        # calculate midpoints
        m1 = point1 + (point2 - point1) / 2
        m2 = point2 + (point3 - point2) / 2

        # Generate perpendicular vectors
        perp_vector_m1 = Vector2(m1.x - point1.y + point2.y, m1.y + point1.x - point2.x)
        perp_line_m1 = Line(origin=Vector2(m1.x, m1.y), destination=perp_vector_m1)

        perp_vector_m2 = Vector2(m2.x - point2.y + point3.y, m2.y + point2.x - point3.x)
        perp_line_m2 = Line(origin=Vector2(m2.x, m2.y), destination=perp_vector_m2)

        # Circle center is where perpendicular vectors intersect
        circ_center = perp_line_m1.intersection(perp_line_m2)

        # Radius is distance from center to one of the boundary points
        rad = (circ_center - point1).length()
        return Circle(circ_center, rad, known_boundary_points=[point1, point2, point3])

    def __init__(self, center: Vector2, radius: float, known_boundary_points: List[Vector2] = None):
        if type(radius) != float:
            raise TypeError(f"Radius must be of type float, but type {type(radius)} was provided")

        self.center = center
        self.radius = radius
        self.known_boundary_points = known_boundary_points if known_boundary_points else []

    def point_at_angle(self, radians: float) -> Vector2:
        x = (self.radius * math.cos(radians) + self.center.x)
        y = (self.radius * math.sin(radians) + self.center.y)
        return Vector2(x, y)

    def rads_of_point(self, point: Vector2):
        rads = math.atan2(point.y - self.center.y, point.x - self.center.x)

        if rads > 0:
            ret = rads
        else:
            ret = 2 * math.pi + rads

        return ret

    def rads_between_points(self, a: Vector2, b: Vector2):
        """Assumes a counter-clockwise orientation between the two points"""
        rad_d = self.rads_of_point(b)
        rad_o = self.rads_of_point(a)

        delta = rad_d - rad_o

        if rad_d > rad_o:
            return delta
        else:
            return 2 * math.pi + delta

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Circle of radius {round(self.radius, 2)} centered at {self.center}"


class Triangle:
    def __init__(self, a: Vector2, b: Vector2, c: Vector2):
        self.area = a.x * (b.y - c.y) + b.x * (c.y - a.y) * c.x * (a.y - b.y)
        if math.isclose(self.area, 0):
            raise ValueError(f"The points [{a}, {b}, {c}] are collinear, the triangle definition is not valid")

        self.points = [a, b, c]

    @property
    def a(self):
        return self.points[0]

    @property
    def b(self):
        return self.points[1]

    @property
    def c(self):
        return self.points[2]

    def incentre(self):
        len_ab = (self.a - self.b).length()
        len_bc = (self.b - self.c).length()
        len_ca = (self.c - self.a).length()

        return (len_bc * self.a + len_ab * self.c + len_ca * self.b) / (len_bc + len_ca + len_ab)


class PolygonRegion:

    @classmethod
    def from_shapely_polygon(cls, shapely_poly: Polygon):
        x, y = shapely_poly.exterior.coords.xy
        return PolygonRegion([Vector2(x[ii], y[ii]) for ii in range(0, len(x))])

    @classmethod
    def convex_hull(self, points: List[Vector2]):
        if not geo.collinear_points([point.as_tuple() for point in points]):
            hull = ConvexHull([point.as_tuple() for point in points])
            return PolygonRegion([points[ind] for ind in hull.vertices])
        else:
            return PolygonRegion(points)


    def __init__(self, boundary_points: List[Vector2] = None):
        self.boundary_points = boundary_points if boundary_points is not None else []

    @property
    def valid(self):
        # valid if at least 3 points and they are not collinear
        return len(self.boundary_points) >= 3 and not geo.collinear_points([point.as_tuple() for point in self.boundary_points])

    def add_points_between_points(self, points: List[Tuple[Vector2, Tuple[Vector2, Vector2]]]):
        for point, between_points in points:

            i0 = self.boundary_points.index(between_points[0])
            i1 = self.boundary_points.index(between_points[1])

            # raise if not consecutive points (index dif should be 1 or len of list for rollover)
            if abs(i1 - i0) != 1 and abs(i1 - i0) != len(self.boundary_points):
                raise ValueError(f"The provided bounding points for point {point} are not at sequential indexes on the boundary [{i0}] and [{i1}]")

            # add point between provided between points
            if abs(i1 - i0) == 1:
                self.boundary_points.insert(min(i0, i1) + 1, point)
            elif abs(i1 - i0) == len(self.boundary_points):
                self.boundary_points.append(point)

    def add_points(self, points: List[Vector2]):
        self.boundary_points += points

    def remove_point(self):
        if len(self.boundary_points) > 0:
            self.boundary_points.pop(-1)

    def intersects(self, other, buffer:float = 0) ->bool:
        if not type(other) == PolygonRegion:
            raise TypeError(f"Cannot find intersection of type {type(self)} with type {type(other)}")


        return Polygon([x.as_tuple() for x in self.boundary_points]).buffer(buffer).intersects(
            Polygon([x.as_tuple() for x in other.boundary_points]).buffer(buffer))

        # intersection = Polygon([x.as_tuple() for x in self.boundary_points]).buffer(buffer).intersection(Polygon([x.as_tuple() for x in other.boundary_points]).buffer(buffer))

        # try:
        #     if intersection is None or intersection.is_empty:
        #         return None
        #     elif intersection.geom_type == "LineString":
        #         x, y = intersection.coords.xy
        #     elif intersection.geom_type == "GeometryCollection":
        #         x, y = intersection.convex_hull.exterior.coords.xy
        #     elif intersection.geom_type == "Point":
        #         x, y = intersection.coords.xy
        #     else:
        #         x, y = intersection.exterior.coords.xy
        # except:
        #     raise Exception(f"Unknown error...")
        #
        # return PolygonRegion([Vector2(x[ii], y[ii]) for ii in range(0, len(x))])

    @property
    def center(self) -> Vector2:
        if len(self.boundary_points) == 0:
            return None

        xs = [point.x for point in self.boundary_points]
        ys = [point.y for point in self.boundary_points]
        cx = sum(xs) / len(xs)
        cy = sum(ys) / len(ys)

        return Vector2(cx, cy)







if __name__ == "__main__":
    rect = Rectangle(100, 10, 25, 50)

    print(rect.center)

    import random as rnd
    points = []
    for ii in range(0, 5):
        points.append(Vector2(rnd.randint(0, 100), rnd.randint(0, 100)))

    poly = PolygonRegion(boundary_points=points)
    print(poly.center)