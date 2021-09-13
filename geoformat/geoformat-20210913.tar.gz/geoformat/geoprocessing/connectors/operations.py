
def coordinates_to_point(coordinates, ):
    """
    With geometry coordinates this function return each point individually in iterator
    :param coordinates
    :yield point coordinate
    """

    if isinstance(coordinates[0], (int, float)):
        yield list(coordinates)
    else:
        for inner_coordinates in coordinates:
            for point in coordinates_to_point(inner_coordinates):
                yield point


def coordinates_to_segment(coordinates):
    """
    This function yield
    :param coordinates:
    :return:
    """
    if isinstance(coordinates[0][0], (float, int)):
        for i, point in enumerate(coordinates_to_point(coordinates)):
            if i == 0:
                pass
            else:
                yield [save_point, point]
            save_point = point
    else:
        for part_coordinates in coordinates:
            for segment in coordinates_to_segment(part_coordinates):
                yield segment


def coordinates_to_bbox(coordinates):
    """
    This function return boundaries box (bbox) from geometry coordinates.
    It's works with 2 to n-dimensional data.
    (x_min, y_min, n_min, x_max, y_max, n_max)

    """
    # if list is not empty
    if coordinates:
        # loop on each coordinates
        bbox = None
        for i_pt, point in enumerate(coordinates_to_point(coordinates)):
            nb_coord = len(point)
            # create bbox structure
            if bbox is None:
                bbox = point * nb_coord
            else:
                # add min and max value of bbox for other coordinates
                for i_coord, coord in enumerate(point):
                    if coord < bbox[i_coord]:
                        bbox[i_coord] = coord
                    if coord > bbox[i_coord + nb_coord]:
                        bbox[i_coord + nb_coord] = coord

        return tuple(bbox)
    else:
        return ()


def segment_to_bbox(segment):
    """
    Return bbox to given segment

    :param segment: segment of which we want to know the bbox
    :return: bbox of segment
    """
    x, y = zip(*segment)

    return min(x), min(y), max(x), max(y)
