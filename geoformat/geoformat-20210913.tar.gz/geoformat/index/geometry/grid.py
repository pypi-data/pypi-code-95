from geoformat.conversion.bbox_conversion import bbox_to_polygon_coordinates
from geoformat.conversion.feature_conversion import feature_serialize
from geoformat.geoprocessing.connectors.operations import coordinates_to_bbox
from geoformat.geoprocessing.geoparameters.bbox import point_bbox_position


########################################################################################################################
#
# GRID INDEX
#
########################################################################################################################


def bbox_to_g_id(bbox, mesh_size, x_grid_origin=0., y_grid_origin=0., grid_precision=None):
    """
    This function allow to find, with bbox coordinates, grid index identifier (g_id) to witch it begins.

    :param bbox: [list/tuple] bbox.
    :param mesh_size: [int] mesh size.
    :param x_grid_origin: x-coordinates of the original point from which the index is constructed.
    :param y_grid_origin: y-coordinates of the original point from which the index is constructed.
    :param grid_precision: precision of grid is the number of digits after the decimal point that we want keep.
    :return: g_id: generator of grid id (g_id) that bbox intersects.
    """

    if grid_precision:
        mesh_size = round(mesh_size, grid_precision)


    (x_min, y_min, x_max, y_max) = bbox
    # gives x_g_id, y_g_id for bbox extremity
    id_x_min = int((x_min - x_grid_origin) / mesh_size)
    if x_min - x_grid_origin < 0:
        id_x_min -= 1
    id_x_max = int((x_max - x_grid_origin) / mesh_size)
    if x_max - x_grid_origin < 0:
        id_x_max -= 1
    id_y_min = int((y_min - y_grid_origin) / mesh_size)
    if y_min - y_grid_origin < 0:
        id_y_min -= 1
    id_y_max = int((y_max - y_grid_origin) / mesh_size)
    if y_max - y_grid_origin < 0:
        id_y_max -= 1

    # recuperate g_id and bbox associate
    g_id_min = (id_x_min, id_y_min)
    g_id_max = (id_x_max, id_y_max)
    bbox_g_id_min = g_id_to_bbox(g_id_min, mesh_size, x_grid_origin=x_grid_origin, y_grid_origin=y_grid_origin, grid_precision=grid_precision)
    bbox_g_id_max = g_id_to_bbox(g_id_max, mesh_size, x_grid_origin=x_grid_origin, y_grid_origin=y_grid_origin, grid_precision=grid_precision)

    # test point position for x_min, y_min if point touch boundary we must change id_x_min and/or id_y_min
    point_position, point_direction = point_bbox_position((x_min, y_min), bbox_g_id_min)
    if point_position.upper() == 'BOUNDARY':  # 'Boundary':
        if point_direction.upper() == 'S':
            id_y_min += - 1
        if point_direction.upper() == 'W':
            id_x_min += - 1
        if point_direction.upper() == "NW":
            id_x_min += - 1
        if point_direction.upper() == "SW":
            id_x_min += - 1
            id_y_min += - 1
        if point_direction.upper() == "SE":
            id_y_min += - 1

    # test point position for x_max, y_max if point touch boundary we must change id_x_max and/or id_y_max
    point_position, point_direction = point_bbox_position((x_max, y_max), bbox_g_id_max)

    if point_position == 'Boundary':
        if point_direction == 'N':
            id_y_max += 1
        if point_direction == 'E':
            id_x_max += 1
        if point_direction == "NE":
            id_x_max += 1
            id_y_max += 1
        if point_direction == "NW":
            id_y_max += 1
        if point_direction == "SE":
            id_x_max += 1

    # double loop sendind all g_id intersecting bbox
    for x_step in range(id_x_min, id_x_max + 1):
        for y_step in range(id_y_min, id_y_max + 1):
            yield (x_step, y_step)


def point_to_g_id(point, mesh_size, x_grid_origin=0., y_grid_origin=0., grid_precision=None):
    """
    This function return grid id (g_id) for a given point.

    :param point: coordinates of point.
    :param mesh_size: size of mesh.
    :param x_grid_origin: coordinate in x of grid origin point.
    :param y_grid_origin: coordinate in y of grid origin point.
    :param grid_precision: precision of grid is the number of digits after the decimal point that we want keep.
    :return: a generator of g_id that intersects input point.
    """
    bbox = point + point

    for g_id in bbox_to_g_id(bbox, mesh_size, x_grid_origin, y_grid_origin, grid_precision=grid_precision):
        yield g_id


def g_id_to_bbox(g_id, mesh_size, x_grid_origin=0., y_grid_origin=0., grid_precision=None):
    """
    This fucntion return the bbox associate to a given g_id (grid id).
    If the grid origin is different to 0. you have to indicate the origin's coordinates (x_grid_origin or y_grid_origin)

    :param g_id: grid mesh identifier.
    :param mesh_size: size of mesh.
    :param x_grid_origin: coordinate in x of grid origin point.
    :param y_grid_origin: coordinate in y of grid origin point.
    :param grid_precision: precision of grid is the number of digits after the decimal point that we want keep.
    :return: bbox of g_id.
    """
    if grid_precision:
        mesh_size = round(mesh_size, grid_precision)
        x_grid_origin = round(x_grid_origin, grid_precision)
        y_grid_origin = round(y_grid_origin, grid_precision)

    (x_id, y_id) = g_id
    x_id, y_id = float(x_id), float(y_id)
    bbox_x_min = x_id * mesh_size
    bbox_x_max = (x_id + 1) * mesh_size
    bbox_y_min = y_id * mesh_size
    bbox_y_max = (y_id + 1) * mesh_size

    if x_grid_origin != 0. or y_grid_origin != 0.:
        bbox_x_min = x_grid_origin + bbox_x_min
        bbox_x_max = x_grid_origin + bbox_x_max
        bbox_y_min = y_grid_origin + bbox_y_min
        bbox_y_max = y_grid_origin + bbox_y_max

    if grid_precision:
        return round(bbox_x_min, grid_precision), round(bbox_y_min, grid_precision), round(bbox_x_max, grid_precision), round(bbox_y_max, grid_precision)
    else:
        return bbox_x_min, bbox_y_min, bbox_x_max, bbox_y_max


def g_id_to_point(g_id, mesh_size, position='center', x_grid_origin=0., y_grid_origin=0., grid_precision=None):
    """
    This function return a coordinates point to given g_id (g_id). Obviously since it is a grid, the position of the
    point can be specified between this values ('center', 'NE', 'NW', 'SE',  'SW').

    If the grid origin is different to 0. you have to indicate the origin's coordinates (x_grid_origin or y_grid_origin)

    :param g_id: g_id you want to get the point of.
    :param mesh_size: size of mesh.
    :param position: position of point in mesh (allowed values are ('center', 'NE', 'NW', 'SE',  'SW')).
    :param x_grid_origin: x coordinates of grid origin.
    :param y_grid_origin: y coordinates of grid origin.
    :param grid_precision: precision of grid is the number of digits after the decimal point that we want keep.
    :return: point coordinates.
    """
    x_min, y_min, x_max, y_max = g_id_to_bbox(g_id, mesh_size)
    position_upper = position.upper()

    if position_upper == 'CENTER':
        x, y = (x_min + x_max) / 2., (y_min + y_max) / 2.
    elif position_upper == 'NE':
        x, y = x_max, y_max
    elif position_upper == 'NW':
        x, y = x_min, y_max
    elif position_upper == 'SE':
        x, y = x_max, y_min
    elif position_upper == 'SW':
        x, y = x_min, y_min
    else:
        raise Exception('ERROR position must be a value between (CENTER, NE, NW, SE or SW)')

    if x_grid_origin != 0. or y_grid_origin != 0.:
        x += x_grid_origin
        y += y_grid_origin

    if grid_precision:
        x, y = round(x, grid_precision), round(y, grid_precision)

    return x, y


def g_id_neighbor_in_grid_index(g_id, grid_index, nb_mesh=1, g_id_include=True):
    """
    Return g_id neighbour if exists in given grid index at a distance of n mesh.

    :param g_id: mesh grid id.
    :param grid_index: grid index.
    :param nb_mesh: distance to find neighbour in mesh unit.
    :param g_id_include: if True output will return g_id value (input parameter).
    :return: generator of g_id neighbour.
    """
    (x_g_id, y_g_id) = g_id

    x_min = x_g_id - nb_mesh
    x_max = x_g_id + nb_mesh + 1
    y_min = y_g_id - nb_mesh
    y_max = y_g_id + nb_mesh + 1
    for x_g_id in range(x_min, x_max):
        for y_g_id in range(y_min, y_max):
            neighbor_g_id = x_g_id, y_g_id
            if neighbor_g_id in grid_index['index']:
                # if neighbor g_id is same that g_id and g_id_include is False we pass
                if g_id_include is False and neighbor_g_id == g_id:
                    pass
                else:
                    yield neighbor_g_id


def create_grid_index(geolayer, mesh_size=None, x_grid_origin=0, y_grid_origin=0, grid_precision=None):
    """
    Create a grid index for a geolayer at a mesh size (deduce automatically or given in input).
    You have also possibility to determine the origin point of the frame on which the grid is constructed (by default
    0, 0).

    This function return a dictionary with this structure : {
        'metadata : {
            'type' :  type of index
            'mesh_size': size of mesh (like in parameters or computed by this function if uninformed)
            'x_grid_origin':  x-coordinates of the original point from which the index is constructed.
                              By default this value is 0.
            'y_grid_origin':  y-coordinates of the original point from which the index is constructed.
                              By default this value is 0.
            'grid_precision': precision of grid is the number of digits after the decimal point that we want keep.
                              By default this value is None.
        'index' : {
            (coordinates of mesh): [list with geolayer i_feat where bbox intersects mesh]
        }

    :param geolayer: geolayer that we want to index
    :param mesh_size: size of mesh
    :param x_grid_origin: x-coordinates of the original point from which the index is constructed.
    :param y_grid_origin: y-coordinates of the original point from which the index is constructed.
    :param grid_precision: precision of grid is the number of digits after the decimal point that we want keep.
     By default this value is None.
    :return: grid index dict (structure describe above)
    """

    # first define mesh size if not yet define
    if not mesh_size:
        # we deduce mean hight and width for all features
        size_x, size_y = 0, 0
        first_point = False
        for i, i_feat in enumerate(geolayer['features']):
            feature = geolayer['features'][i_feat]

            # if feature is serialized
            if 'feature_serialize' in geolayer['metadata']:
                if geolayer['metadata']['feature_serialize']:
                    feature = eval(feature)
            # get bbox
            try:
                bbox = feature['geometry']['bbox']
            except KeyError:
                bbox = coordinates_to_bbox(feature['geometry']['coordinates'])
                feature['geometry']['bbox'] = bbox

            # if geometry type is point there is no dimension in same bbox (no lenght / no width) we have to compare
            #  with others points bbox
            if feature['geometry']['type'] == 'Point':
                if not first_point:
                    old_point_bbox = bbox
                    first_point = True
                else:
                    size_x += abs(bbox[2] - old_point_bbox[2])
                    size_y += abs(bbox[3] - old_point_bbox[3])
                    old_point_bbox = bbox

            else:
                size_x += bbox[2] - bbox[0]
                size_y += bbox[3] - bbox[1]

        mesh_size = max(size_x / len(geolayer['features']), size_y / len(geolayer['features']))

    index_dict = {}
    # add metadata
    index_dict['metadata'] = {'type': 'grid',
                              'mesh_size': mesh_size,
                              'x_grid_origin': x_grid_origin,
                              'y_grid_origin': y_grid_origin,
                              'grid_precision': grid_precision}
    index_dict['index'] = {}

    for i_feat in geolayer['features']:
        feature = geolayer['features'][i_feat]

        # if feature is serialized
        if 'feature_serialize' in geolayer['metadata']:
            if geolayer['metadata']['feature_serialize']:
                feature = eval(feature)

        geom = feature['geometry']

        if 'bbox' in geom.keys():
            bbox_geom = geom['bbox']
        else:
            coordinates = geom['coordinates']
            bbox_geom = coordinates_to_bbox(coordinates)

        # for each grid identifier (g_id) we add in grid_idx_dico entity identifier (i_feat)
        for g_id in bbox_to_g_id(bbox=bbox_geom,
                                 mesh_size=mesh_size,
                                 x_grid_origin=x_grid_origin,
                                 y_grid_origin=y_grid_origin,
                                 grid_precision=grid_precision):
            try:
                index_dict['index'][g_id].append(i_feat)
            except KeyError:
                index_dict['index'][g_id] = [i_feat]

    return index_dict


def grid_index_to_geolayer(grid_index, name='grid_index', crs=None, features_serialize=False):
    """
    Create geolayer associate to grid index.

    :param grid_index: reference grid index
    :param name: name of geolayer
    :param crs: coordinates reference system
    :param features_serialize: True feature will be serialized / False feature are not serializes
    :return:  geolayer associate to grid index
    """

    geolayer = {'features': {}, 'metadata': {'name': name, 'geometry_ref': {'type': 'Polygon'}, }}

    if crs:
        geolayer['metadata']['geometry_ref']['crs'] = crs

    # create field
    geolayer['metadata']['fields'] = {'g_id': {'type': 'String', 'width': 254, 'index': 0},
                                      'i_feat_list': {'type': 'IntegerList', 'index': 1}}
    # add feature
    for i_feat, g_id in enumerate(grid_index['index']):
        feature = {
            'attributes': {'g_id': g_id, 'i_feat_list': grid_index['index'][g_id]},
            'geometry': {
                'type': 'Polygon',
                'coordinates': bbox_to_polygon_coordinates(
                    g_id_to_bbox(
                        g_id,
                        mesh_size=grid_index['metadata']['mesh_size'],
                        x_grid_origin=grid_index['metadata']['x_grid_origin'],
                        y_grid_origin=grid_index['metadata']['y_grid_origin']
                    )
                )
            }
        }

        if features_serialize:
            feature = feature_serialize(feature)

        geolayer['features'][i_feat] = feature

    return geolayer