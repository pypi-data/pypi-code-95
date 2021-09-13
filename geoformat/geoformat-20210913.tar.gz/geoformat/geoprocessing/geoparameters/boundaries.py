from geoformat.geoprocessing.measure.area import shoelace_formula


def ccw_or_cw_boundary(boundary_coordinates):
    """
    The aim of this function is to determinate if boundary[1] of polygon is counter clock wise [CCW] or clock wise [CW].
    To do that we use : Shoelace Formula to determine the area of polygon.

    [1] = here we talk about boundary not entire polygon. We voluntary separate, boundary and hole in polygon, because
    logicaly a boundary can have a sens and the hole can have an other sens. So if you want to know polygon sens you
    have to test separately boundary and hole.

        Input:
            ring_coordinates(list/tuple) :  boundary coordinates

        Output:
            sens: CCW: counter clock wise OR CW clock wise
    """

    if shoelace_formula(boundary_coordinates, False) < 0:
        return 'CCW'
    else:
        return 'CW'
