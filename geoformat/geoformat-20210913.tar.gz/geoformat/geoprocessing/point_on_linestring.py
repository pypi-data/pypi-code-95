from geoformat.geoprocessing.geoparameters.lines import (
    line_parameters,
    point_at_distance_with_line_parameters,
    perpendicular_line_parameters_at_point
)
from geoformat.geoprocessing.measure.distance import (
    euclidean_distance
)

from geoformat.conversion.geometry_conversion import geometry_to_multi_geometry


def point_at_a_distance_on_segment(segment, step_distance, offset_distance=None):
    """
    Iterator send point coordinates on a segment at a given step distance.
    optional: add an offset distance (perpendicular to line_parameters value)

    :param segment:
    :param step_distance:
    :param offset_distance:
    :return:
    """
    # initialize
    native_step_distance = step_distance

    # split segment to point
    start_point, end_point = segment
    # get segment line parameter
    segment_line_parameter = line_parameters(segment)

    # recompute start point and end point and line parameters if offset is required
    if offset_distance:
        start_point = point_at_distance_with_line_parameters(
            start_point,
            segment_line_parameter,
            0,
            offset_distance=offset_distance
        )
        end_point = point_at_distance_with_line_parameters(
            end_point,
            segment_line_parameter,
            0,
            offset_distance=offset_distance
        )
        segment_line_parameter = line_parameters((start_point, end_point))

    # segment_line_parameter slope determine line orientation (from left to the right)
    # we need to to determine the direction on this slope between start_point and end_point
    point_at_a_distance = point_at_distance_with_line_parameters(
        start_point=end_point,
        line_parameters=segment_line_parameter,
        distance=step_distance,
    )

    length_between_start_point_and_point_at_distance = euclidean_distance(
        point_a=start_point,
        point_b=point_at_a_distance
    )
    segment_length = euclidean_distance(
        point_a=start_point,
        point_b=end_point
    )

    if length_between_start_point_and_point_at_distance < segment_length:
        step_distance = -step_distance

    while segment_length >= native_step_distance:
        # compute new start point at a distance
        start_point = point_at_distance_with_line_parameters(
            start_point=start_point,
            line_parameters=segment_line_parameter,
            distance=step_distance
        )
        yield start_point
        # recompute segment length with new start_point
        segment_length = euclidean_distance(
            point_a=start_point,
            point_b=end_point
        )


def points_on_linestring_distance(linestring, step_distance, offset_distance=None):
    """
    Return a point geometry that is a point on a given linestring at a given step_distance
    optional: add an offset distance (perpendicular to line_parameters value)

    :param linestring: LineString or MultiLineString geometry
    :param step_distance: distance between each steps
    :param offset_distance: if you want you can add an offset to final on point value
    :return: Point geometry
    """

    def points_on_linestring_part(coordinates, step_distance, offset_distance=None):

        # note about remaining_distance
        # remaining_distance is the distance that remain after a new vertex (because when there is a new vertex we have
        # to recompute the step_distance remaining

        # loop on each coordinate
        for i_point, point in enumerate(coordinates):
            if i_point == 0:
                previous_point = point
                # init remaining distance
                remaining_distance = 0
            else:
                remaining_step_distance = step_distance - remaining_distance
                segment = (previous_point, point)

                # yield first point
                if i_point == 1:
                    first_point_geometry = {'type': 'Point'}
                    if offset_distance:
                        line_parameter = line_parameters(segment)
                        perp_parameter = perpendicular_line_parameters_at_point(line_parameter, previous_point)
                        first_point = point_at_distance_with_line_parameters(previous_point, perp_parameter,
                                                                             distance=offset_distance)
                        first_point_geometry['coordinates'] = list(first_point)
                    else:
                        first_point_geometry['coordinates'] = list(previous_point)

                    yield first_point_geometry

                # for just one iteration
                for new_point in point_at_a_distance_on_segment(segment, remaining_step_distance, offset_distance=None):
                    remaining_distance = 0
                    # reinit values
                    previous_point = new_point
                    segment = (previous_point, point)
                    # here we cannot use offset_distance directly in point_at_a_distance_on_segment used above because
                    # we have to keep initial segment direction. Then we recompute offset new_point.
                    if offset_distance:
                        line_parameter = line_parameters(segment)
                        perp_parameter = perpendicular_line_parameters_at_point(line_parameter, new_point)
                        new_point = point_at_distance_with_line_parameters(new_point, perp_parameter,
                                                                           distance=offset_distance)
                    yield {'type': 'Point', 'coordinates': list(new_point)}
                    break  # just one iteration

                # pass_on_loop check if we iterate on loop below
                pass_on_loop = False
                for new_point in point_at_a_distance_on_segment(segment, step_distance, offset_distance=None):
                    remaining_distance = euclidean_distance(new_point, point)
                    pass_on_loop = True
                    # here we cannot use offset_distance directly in point_at_a_distance_on_segment used above because
                    # we have to calculate the remain distance on non offseted point before. Then we recompute offset
                    # new_point
                    if offset_distance:
                        line_parameter = line_parameters(segment)
                        perp_parameter = perpendicular_line_parameters_at_point(line_parameter, new_point)
                        new_point = point_at_distance_with_line_parameters(new_point, perp_parameter,
                                                                           distance=offset_distance)
                    yield {'type': 'Point', 'coordinates': list(new_point)}

                # if no iteration en loop above we recalculate remaining distance for next point on coordinates
                if not pass_on_loop:
                    remaining_distance += euclidean_distance(point, previous_point)

                previous_point = point

    # force linestring to multilinestring
    multilinestring = geometry_to_multi_geometry(geometry=linestring, bbox=False)

    for linestring_part in multilinestring['coordinates']:
        for point in points_on_linestring_part(linestring_part, step_distance, offset_distance=offset_distance):
            yield point

