
def extent_bbox(bbox, extent):
    """
    Realize ratio enlargement or reduction of a given bbox

    :param bbox: input bbox
    :param extent:  size of enlargement (positive) or reduction (negative)
    :return: enlarge or reduce bbox
    """
    if bbox:
        (x_min, y_min, x_max, y_max) = bbox
    else:
        x_min, y_min, x_max, y_max = (0, 0, 0, 0)

    x_min = x_min - extent
    y_min = y_min - extent
    x_max = x_max + extent
    y_max = y_max + extent

    return x_min, y_min, x_max, y_max

def bbox_union(bbox_a, bbox_b):
    """
    realize union between two given bbox

    :param bbox_a: first bbox
    :param bbox_b: second bbox
    :return: unioned bbox
    """
    if bbox_a and bbox_b:
        (x_min_a, y_min_a, x_max_a, y_max_a) = bbox_a
        (x_min_b, y_min_b, x_max_b, y_max_b) = bbox_b

        bbox = min(x_min_a, x_min_b), min(y_min_a, y_min_b), max(x_max_a, x_max_b), max(y_max_a, y_max_b)
    elif bbox_a and not bbox_b:
        bbox = bbox_a
    elif bbox_b and not bbox_a:
        bbox = bbox_b
    elif not bbox_a and not bbox_b:
        bbox = ()

    return bbox


def point_bbox_position(point, bbox):
    """
    Return point position and sector (NW, N, NE, W, E, SW, S, SE) in regard to given bbox.

    Diagram showing sectors's position around a bbox :

       NW  |   N  |  NE
    -------+------+-------
        W  | bbox |   E
    -------+------+-------
       SW  |   S  |  SE

    3 position possibilities and sectors configuration :
        * Boundary : and side of bbox boundary (N, S, E, W) or corner (NW, NE, SW, SE)
        * Exterior : (NW, N, NE, W, E, SW, S, SE)
        * Interior : None

    """

    (pt_x, pt_y) = point
    (x_min, y_min, x_max, y_max) = bbox

    # North
    if (pt_x > x_min and pt_x < x_max) and (pt_y >= y_max):
        if pt_y == y_max:
            position = ('Boundary', 'N')
        else:
            position = ('Exterior', 'N')
    # South
    elif (pt_x > x_min and pt_x < x_max) and (pt_y <= y_min):
        if pt_y == y_min:
            position = ('Boundary', 'S')
        else:
            position = ('Exterior', 'S')
    # Est
    elif pt_x >= x_max and (pt_y > y_min and pt_y < y_max):
        if pt_x == x_max:
            position = ('Boundary', 'E')
        else:
            position = ('Exterior', 'E')
    # West
    elif pt_x <= x_min and (pt_y > y_min and pt_y < y_max):
        if pt_x == x_min:
            position = ('Boundary', 'W')
        else:
            position = ('Exterior', 'W')
    # North-West
    elif pt_x <= x_min and pt_y >= y_max:
        if pt_x == x_min and pt_y == y_max:
            position = ('Boundary', 'NW')
        else:
            position = ('Exterior', 'NW')
    # North-Est
    elif pt_x >= x_max and pt_y >= y_max:
        if pt_x == x_max and pt_y == y_max:
            position = ('Boundary', 'NE')
        else:
            position = ('Exterior', 'NE')
    # South-Est
    elif pt_x >= x_max and pt_y <= y_min:
        if pt_x == x_max and pt_y == y_min:
            position = ('Boundary', 'SE')
        else:
            position = ('Exterior', 'SE')
    # South-West
    elif pt_x <= x_min and pt_y <= y_min:
        if pt_x == x_min and pt_y == y_min:
            position = ('Boundary', 'SW')
        else:
            position = ('Exterior', 'SW')
    # Point in bbox
    else:
        position = ('Interior', None)

    return position

