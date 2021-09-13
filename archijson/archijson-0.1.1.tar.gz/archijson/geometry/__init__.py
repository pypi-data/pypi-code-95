from geometry.base import BasePoint, BaseGeometry
from geometry.shape import Cuboid, Cylinder, Plane
from geometry.mesh import Vertices, Segments, Faces, Mesh

call = {
    'Cuboid': Cuboid,
    'Cylinder': Cylinder,
    'Plane': Plane,
    'Vertices': Vertices,
    'Segments': Segments,
    'Faces': Faces,
    'Mesh': Mesh,
}
