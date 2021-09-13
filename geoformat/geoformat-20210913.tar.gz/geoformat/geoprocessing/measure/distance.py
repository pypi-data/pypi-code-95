from geoformat.geoprocessing.connectors.operations import segment_to_bbox
from geoformat.geoprocessing.geoparameters.lines import (
    line_parameters,
    perpendicular_line_parameters_at_point,
    crossing_point_from_lines_parameters
)


def euclidean_distance(point_a, point_b):
    """
    retunn Euclidean distance between two points

    :param point_a:
    :param point_b:
    :return: Euclidean distance between two points
    """
    (x_a, y_a) = point_a
    (x_b, y_b) = point_b
    return ((x_b - x_a) ** 2 + (y_b - y_a) ** 2) ** 0.5


def manhattan_distance(point_a, point_b):
    """
    return Manhattan distance between to points

    :param point_a:
    :param point_b:
    :return: Manhattan distance between to points
    """
    x1, y1 = point_a
    x2, y2 = point_b
    return float(abs(x1 - x2) + abs(y1 - y2))


def euclidean_distance_point_vs_segment(point, segment):
    """
    Calculate distance between a point and a segment

    adapted from : https://stackoverflow.com/questions/849211/shortest-distance-between-a-point-and-a-line-segment

    Much more faster than point_vs_segment_distance

    :param point: vertex coordinate
    :param segment: segment coordinates
    :return: distance between point and segment
    """

    ((x1, y1), (x2, y2)) = segment
    (x3, y3) = point

    px = x2-x1
    py = y2-y1

    something = px*px + py*py

    # if segment is actually a point
    if something == 0:
        dist = euclidean_distance(point_a=point, point_b=segment[0])
    else:
        u = ((x3 - x1) * px + (y3 - y1) * py) / float(something)

        if u > 1:
            u = 1
        elif u < 0:
            u = 0

        x = x1 + u * px
        y = y1 + u * py

        dx = x - x3
        dy = y - y3

        # Note: If the actual distance does not matter,
        # if you only want to compare what this function
        # returns to other results of this function, you
        # can just return the squared distance instead

        dist = (dx*dx + dy*dy) ** 0.5

    return dist


def point_vs_segment_distance(point, segment, distance_function=euclidean_distance):
    """
    Calculate distance between a point and a segment, distance can be define with distance function parameter (default :
    euclidean)

    :param point:
    :param segment:
    :param distance_function:
    :return:
    """
    # get line parameter to segment
    segment_line_parameters = line_parameters(segment)
    # get perpendicular parameters to line parameters above
    perpendicular_line_parameters = perpendicular_line_parameters_at_point(line_parameters=segment_line_parameters,
                                                                           point=point)
    # get intersection
    intersection_point = crossing_point_from_lines_parameters(line_parameter_a=segment_line_parameters,
                                                              line_parameter_b=perpendicular_line_parameters)
    # get segment bbox
    segment_bbox = segment_to_bbox(segment)
    # if point is in bbox (we use bbox for floating point precision consideration)
    if segment_bbox[0] <= intersection_point[0] <= segment_bbox[2] and segment_bbox[1] <= intersection_point[1] <= segment_bbox[3]:
        return distance_function(point, intersection_point)
    # else we have to calculate distance between start and end point to segment (we return minimal distance)
    else:
        start_point = segment[0]
        end_point = segment[1]
        return min(distance_function(point, start_point), distance_function(point, end_point))
