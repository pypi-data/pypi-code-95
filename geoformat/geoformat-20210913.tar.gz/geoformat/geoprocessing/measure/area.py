from geoformat.geoprocessing.measure.distance import (
    euclidean_distance_point_vs_segment
)


def shoelace_formula(ring_coordinates, absolute_value=True):
    """
    This function give the area of a boundary in the unit of coordinates.
    It is useful to use shoelace_formula to determine encoding sens of boundary coordinates
    (see ccw_or_cw_boundary)

    :param ring_coordinates: list of coordinates
    :param absolute_value: True / False
    :return: ring area (in coordinates unit)
    """
    nb_vertex = len(ring_coordinates)
    nb_edge = nb_vertex - 1

    l = [(ring_coordinates[i + 1][0] - ring_coordinates[i][0]) * (
            ring_coordinates[i + 1][1] + ring_coordinates[i][1]) for i in range(nb_edge)]

    if absolute_value:
        return abs(sum(l) / 2)
    else:
        return sum(l) / 2


def triangle_area(vertex_a, vertex_b, vertex_c):
    """
    This function return triangle's air composed of these three inputs vertex

    :param vertex_a: first vertex
    :param vertex_b: second vertex
    :param vertex_c: third vertex
    :return: triangle area
    """

    base = ((vertex_b[0] - vertex_a[0]) ** 2 + (vertex_b[1] - vertex_a[1]) ** 2) ** 0.5
    height = euclidean_distance_point_vs_segment(segment=(vertex_a, vertex_b), point=vertex_c)
    air = (height * base) / 2.

    return air
