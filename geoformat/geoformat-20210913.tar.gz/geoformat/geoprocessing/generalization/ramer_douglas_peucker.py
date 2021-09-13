from geoformat.geoprocessing.measure.distance import (
    euclidean_distance_point_vs_segment
)


def ramer_douglas_peucker(coordinate_list, tolerance):
    """
    This function is a generalizatio algorithm.
    It's take a coordinate's list and a tolerance value and return a simplified coordinate's list

        https://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm

    :param coordinate_list: coordinate's list
    :param tolerance: maximum distance in coordinates units
    :return: simplified coordinates
    """

    # if coordinates_list is not empty and have more than 2 coordinates
    if len(coordinate_list) > 2:
        # get coordinates_list extremity points
        point_start = coordinate_list[0]
        point_end = coordinate_list[-1]

        # create segment with extremity points
        segment = [point_start, point_end]

        # initialize coordinate variables
        distance_max_point_segment = 0
        index_max_point_segment = None
        coordinate_list_without_start_end_points = coordinate_list[1:-1]

        for i_point, point in enumerate(coordinate_list_without_start_end_points):
            distance_point_segment = euclidean_distance_point_vs_segment(point, segment)
            if distance_point_segment > tolerance:
                if distance_point_segment > distance_max_point_segment:
                    distance_max_point_segment = distance_point_segment
                    index_max_point_segment = i_point

        if index_max_point_segment is None:
            coordinate_list_result = segment
        else:
            coordinate_list_start = [point_start] + coordinate_list_without_start_end_points[:index_max_point_segment+1]
            coordinate_list_end = coordinate_list_without_start_end_points[index_max_point_segment:] + [point_end]
            segment_start = ramer_douglas_peucker(coordinate_list=coordinate_list_start, tolerance=tolerance)
            segment_end = ramer_douglas_peucker(coordinate_list=coordinate_list_end, tolerance=tolerance)
            coordinate_list_result = segment_start[:-1] + segment_end
    else:
        coordinate_list_result = coordinate_list

    return coordinate_list_result

