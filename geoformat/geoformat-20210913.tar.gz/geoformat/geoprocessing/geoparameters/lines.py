def get_slope_between_two_points(point_a, point_b):
    """
    Return slope value for a line that pass between two input points

    :param point_a: first input point
    :param point_b: second input point
    :return:  slope value
    """
    x_a, y_a = point_a
    x_b, y_b = point_b
    if x_a != x_b:
        slope = (y_b - y_a) / (x_b - x_a)
    else:
        slope = 'VERTICAL'

    return slope


def get_intercept_from_point_and_slope(point, slope):
    """
    return intercept value from a line that pass to input point with input slope

    :param point: point
    :param slope: slope value
    :return: intercept value that pass to input point with input slope
    """

    point_x, point_y = point

    # if slope is horizontal or vertical
    if slope == 0 or slope == 'VERTICAL':
        intercept = point_y
    else:
        intercept = slope * (0 - point_x) + point_y

    return intercept


def get_slope_from_point_and_intercept(point, intercept):
    """
    return slope value from a line that pass by input point and that intercepts y axis to input intercept value

    :param point:
    :param intercept:
    :return:
    """

    # if intercept is False slope is vertical
    if intercept is False:
        point_intercept = point
    else:
        point_intercept = 0, intercept

    return get_slope_between_two_points(point, point_intercept)


def line_parameters(segment):
    """
    Deduces from a segment lines (slope and  intercept) parameters passing through this segment

    :param segment: input segment
    :return: a dict with two linears parameters : slope AND y_intercept
    """

    ((x_a, y_a), (x_b, y_b)) = segment
    if x_b != x_a:
        a = (y_b - y_a) / (x_b - x_a)
        b = y_a - (x_a * a)
    else:
        a = 'VERTICAL'
        b = x_a

    return {'slope': a, 'intercept': b}


def perpendicular_line_parameters_at_point(line_parameters, point):
    """
    Gives perpendicular lines parameters of a line passing through a point from an original line parameters

    :param line_parameters: original line parameter
    :param point: point of origin which serves as a pivot for calculating the parameters of perpendicular lines
    :return:
    """

    a = line_parameters['slope']

    x_a, y_a = point
    if a == 0.:
        a_bis = 'VERTICAL'
        b_bis = x_a
    elif a == 'VERTICAL':
        a_bis = 0.
        b_bis = y_a
    else:
        a_bis = -1 / a
        b_bis = y_a - (x_a * a_bis)

    return {"slope": a_bis, 'intercept': b_bis}


def point_at_distance_with_line_parameters(start_point, line_parameters, distance, offset_distance=None):
    """
    Returns a point at distance to a input_point with a direction define by line parameters.
    Distance can be negative.
    optional: add an offset distance (perpendicular to line_parameters value)

    :param start_point: input start_point
    :param line_parameters: line parameter that define direction to the new start_point
    :param distance: distance between input start_point to output start_point
    :param offset_distance: in option you can add a perpendicular offset input start_point
    :return: output start_point
    """

    slope = line_parameters['slope']
    intercept = line_parameters['intercept']

    x_a, y_a = start_point
    if slope == 'VERTICAL':
        x_b = x_a
        y_b = y_a + distance
    else:
        x_b = x_a + (distance / ((1 + slope ** 2) ** 0.5))
        y_b = slope * x_b + intercept

    ouput_point = x_b, y_b

    if offset_distance:
        perpendicular_parameter = perpendicular_line_parameters_at_point(line_parameters=line_parameters,
                                                                         point=ouput_point)
        offset_x, offset_y = point_at_distance_with_line_parameters(start_point=ouput_point,
                                                                    line_parameters=perpendicular_parameter,
                                                                    distance=offset_distance,
                                                                    offset_distance=None)
        ouput_point = offset_x, offset_y

    return ouput_point


def crossing_point_from_lines_parameters(line_parameter_a, line_parameter_b):
    """
    Return point coordinates that crossing two lines (if possible: slope must be different).
    If lines are parallel the function returns None

    :param line_parameter_a: parameters for line a
    :param line_parameter_b: parameters for line b
    :return: intersecting point between two lines
    """
    # slope must be different
    if line_parameter_a['slope'] != line_parameter_b['slope']:
        # define x
        if line_parameter_a['slope'] == 'VERTICAL':
            point_x = line_parameter_a['intercept']
        elif line_parameter_b['slope'] == 'VERTICAL':
            point_x = line_parameter_b['intercept']
        else:
            point_x = (line_parameter_a['intercept'] - line_parameter_b['intercept']) / (line_parameter_b['slope'] - line_parameter_a['slope'])

        # define y
        if line_parameter_a['slope'] == 'VERTICAL':
            point_y = line_parameter_b['slope'] * point_x + line_parameter_b['intercept']
        else:
            point_y = line_parameter_a['slope'] * point_x + line_parameter_a['intercept']

        return point_x, point_y
