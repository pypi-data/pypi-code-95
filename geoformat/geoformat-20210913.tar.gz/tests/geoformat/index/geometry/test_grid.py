import random

from geoformat.explore_data.random_geometry import (
    random_point,
    random_segment,
    random_bbox
)
from geoformat.geoprocessing.connectors.operations import segment_to_bbox
from geoformat.geoprocessing.connectors.predicates import (
    point_intersects_bbox,
    bbox_intersects_bbox
)
from geoformat.index.geometry.grid import (
    bbox_to_g_id,
    point_to_g_id,
    g_id_to_bbox,
    g_id_to_point,
    g_id_neighbor_in_grid_index,
    create_grid_index,
    grid_index_to_geolayer
)
from tests.data.geolayers import (
    geolayer_for_index,
    geolayer_for_index_grid_geolayer,
    geolayer_for_index_width,
    geolayer_for_index_width_grid_geolayer,
    geolayer_for_index_height,
    geolayer_for_index_height_grid_geolayer,
    geolayer_for_index_width_height,
    geolayer_for_index_width_height_grid_geolayer
)

from tests.data.geometry_index import (
    geolayer_for_index_grid_index,
    geolayer_for_index_width_grid_index,
    geolayer_for_index_height_grid_index,
    geolayer_for_index_width_height_grid_index
)

from test_all import test_function

bbox_to_g_id_parameters = {
    0: {
        "bbox": (-9, -9, 9, 9),
        "mesh_size": 10,
        "x_grid_origin": 0.,
        "y_grid_origin": 0.,
        "grid_precision": None,
        "return_value": ((-1, -1), (-1, 0), (0, -1), (0, 0),)
    },
    1: {
        "bbox": (-9, -9, 9, 9),
        "mesh_size": 10,
        "x_grid_origin": 9,
        "y_grid_origin": 9,
        "grid_precision": None,
        "return_value": ((-2, -2), (-2, -1), (-2, 0), (-1, -2), (-1, -1), (-1, 0), (0, -2), (0, -1), (0, 0))
    },
    2: {
        "bbox": (2, 1, 5, 3.3333332),
        "mesh_size": 10/3,
        "x_grid_origin": 0,
        "y_grid_origin": 0,
        "grid_precision": None,
        "return_value": ((0, 0), (1, 0))
    },
    3: {
        "bbox": (2, 1, 5, 3.3333332),
        "mesh_size": 10/3,
        "x_grid_origin": 0,
        "y_grid_origin": 0,
        "grid_precision": 2,
        "return_value": ((0, 0), (0, 1), (1, 0), (1, 1))
    },
}

point_to_g_id_parameters = {
    0: {
        "point": (168158.34003543295, 5388929.476522685),
        "mesh_size": 30,
        "x_grid_origin": 0,
        "y_grid_origin": 0,
        "return_value": ((5605, 179630),),
    },
    1: {
        "point": (10, 10),
        "mesh_size": 10,
        "x_grid_origin": 0,
        "y_grid_origin": 0,
        "return_value": ((0, 0), (0, 1), (1, 0), (1, 1)),
    },
    2: {
        "point": (0, 0),
        "mesh_size": 10,
        "x_grid_origin": 0,
        "y_grid_origin": 0,
        "return_value": ((-1, -1), (-1, 0), (0, -1), (0, 0)),
    },
    3: {
        "point": (0, 10),
        "mesh_size": 10,
        "x_grid_origin": 0,
        "y_grid_origin": 0,
        "return_value": ((-1, 0), (-1, 1), (0, 0), (0, 1)),
    },
    4: {
        "point": (10, 0),
        "mesh_size": 10,
        "x_grid_origin": 0,
        "y_grid_origin": 0,
        "return_value": ((0, -1), (0, 0), (1, -1), (1, 0)),
    },
    5: {
        "point": (5, 10),
        "mesh_size": 10,
        "x_grid_origin": 0,
        "y_grid_origin": 0,
        "return_value": ((0, 0), (0, 1)),
    },
    6: {
        "point": (5, 0),
        "mesh_size": 10,
        "x_grid_origin": 0,
        "y_grid_origin": 0,
        "return_value": ((0, -1), (0, 0)),
    },
    7: {
        "point": (0, 5),
        "mesh_size": 10,
        "x_grid_origin": 0,
        "y_grid_origin": 0,
        "return_value": ((-1, 0), (0, 0)),
    },
    8: {
        "point": (10, 5),
        "mesh_size": 10,
        "x_grid_origin": 0,
        "y_grid_origin": 0,
        "return_value": ((0, 0), (1, 0)),
    },
    9: {
        "point": (5, 5),
        "mesh_size": 10,
        "x_grid_origin": 5,
        "y_grid_origin": 5,
        "return_value": ((-1, -1), (-1, 0), (0, -1), (0, 0)),
    },
    10: {
        "point": (-76226, 5597112),
        "mesh_size": 30,
        "x_grid_origin": 0,
        "y_grid_origin": 0,
        "return_value": ((-2541, 186570),)
    },
    11: {
        "point": (-33.07, 28.2),
        "mesh_size": 2.35,
        "x_grid_origin": 0,
        "y_grid_origin": 0,
        "grid_precision": None,
        "return_value": ((-15, 12),)
    },
    12: {
        "point": (-33.07, 28.2),
        "mesh_size": 2.35,
        "x_grid_origin": 0,
        "y_grid_origin": 0,
        "grid_precision": 8,
        "return_value": ((-15, 11), (-15, 12))
    },
    13: {
        "point": (0, 0),
        "mesh_size": 2,
        "x_grid_origin": 0,
        "y_grid_origin": 0,
        "return_value": ((-1, -1), (-1, 0), (0, -1), (0, 0))
    },
    14: {
        "point": (0, 1),
        "mesh_size": 2,
        "x_grid_origin": 0,
        "y_grid_origin": 0,
        "return_value": ((-1, 0), (0, 0))
    },
    15: {
        "point": (1, 1),
        "mesh_size": 2,
        "x_grid_origin": 0,
        "y_grid_origin": 0,
        "return_value": ((0, 0),)
    },
    16: {
        "point": (1, 0),
        "mesh_size": 2,
        "x_grid_origin": 0,
        "y_grid_origin": 0,
        "return_value": ((0, -1), (0, 0))
    },
    17: {
        "point": (1, -1),
        "mesh_size": 2,
        "x_grid_origin": 0,
        "y_grid_origin": 0,
        "return_value": ((0, -1),)
    },
    18: {
        "point": (0, -1),
        "mesh_size": 2,
        "x_grid_origin": 0,
        "y_grid_origin": 0,
        "return_value": ((-1, -1), (0, -1))
    },
    19: {
        "point": (-1, -1),
        "mesh_size": 2,
        "x_grid_origin": 0,
        "y_grid_origin": 0,
        "return_value": ((-1, -1),)
    },
    20: {
        "point": (-1, 0),
        "mesh_size": 2,
        "x_grid_origin": 0,
        "y_grid_origin": 0,
        "return_value": ((-1, -1), (-1, 0))
    },
    21: {
        "point": (-1, 1),
        "mesh_size": 2,
        "x_grid_origin": 0,
        "y_grid_origin": 0,
        "return_value": ((-1, 0),)
    }
}

g_id_to_bbox_parameters = {
    0: {
        "g_id": (0, 0),
        "mesh_size": 10,
        "x_grid_origin": 0.,
        "y_grid_origin": 0.,
        "grid_precision": None,
        "return_value": (0, 0, 10, 10)
    },
    1: {
        "g_id": (0, 0),
        "mesh_size": 10,
        "x_grid_origin": 10,
        "y_grid_origin": -10,
        "grid_precision": None,
        "return_value": (10, -10, 20, 0)
    },
    2: {
        "g_id": (0, 0),
        "mesh_size": 3 / 9,
        "x_grid_origin": 0,
        "y_grid_origin": 0,
        "grid_precision": 4,
        "return_value": (0, 0, 0.3333, 0.3333)
    },
    3: {
        "g_id": (0, 0),
        "mesh_size": 3 / 9,
        "x_grid_origin": 0,
        "y_grid_origin": 0,
        "grid_precision": 8,
        "return_value": (0, 0, 0.33333333, 0.33333333)
    },
}


g_id_to_point_parameters = {
    0: {
        "g_id": (0, 0),
        "mesh_size": 10,
        "position": "center",
        "x_grid_origin": 0.,
        "y_grid_origin": 0.,
        "grid_precision": None,
        "return_value": (5, 5)
    },
    1: {
        "g_id": (0, 0),
        "mesh_size": 10,
        "position": "center",
        "x_grid_origin": 10,
        "y_grid_origin": -10,
        "grid_precision": None,
        "return_value": (15, -5)
    },
    2: {
        "g_id": (0, 0),
        "mesh_size": 3 / 9,
        "position": "center",
        "x_grid_origin": 0,
        "y_grid_origin": 0,
        "grid_precision": 4,
        "return_value": (0.1667, 0.1667)
    },
    3: {
        "g_id": (0, 0),
        "mesh_size": 3 / 9,
        "position": "center",
        "x_grid_origin": 0,
        "y_grid_origin": 0,
        "grid_precision": 8,
        "return_value": (0.16666667, 0.16666667)
    },
    4: {
        "g_id": (-10, -10),
        "mesh_size": 10,
        "position": "center",
        "x_grid_origin": 0.,
        "y_grid_origin": 0.,
        "grid_precision": None,
        "return_value": (-95., -95.)
    },
    5: {
        "g_id": (-10, -10),
        "mesh_size": 10,
        "position": "NW",
        "x_grid_origin": 0.,
        "y_grid_origin": 0.,
        "grid_precision": None,
        "return_value": (-100, -90)
    },
    6: {
        "g_id": (-10, -10),
        "mesh_size": 10,
        "position": "NE",
        "x_grid_origin": 0.,
        "y_grid_origin": 0.,
        "grid_precision": None,
        "return_value": (-90, -90)
    },
    7: {
        "g_id": (-10, -10),
        "mesh_size": 10,
        "position": "SW",
        "x_grid_origin": 0.,
        "y_grid_origin": 0.,
        "grid_precision": None,
        "return_value": (-100, -100)
    },
    8: {
        "g_id": (-10, -10),
        "mesh_size": 10,
        "position": "SE",
        "x_grid_origin": 0.,
        "y_grid_origin": 0.,
        "grid_precision": None,
        "return_value": (-90, -100)
    },
}

g_id_neighbor_in_grid_index_parameters = {
    0: {
        "g_id": (-10, -3),
        "grid_index": create_grid_index(geolayer_for_index, mesh_size=1),
        "nb_mesh": 1,
        "g_id_include": True,
        "return_value": ((-11, -4), (-11, -3), (-10, -4), (-10, -3), (-9, -4), (-9, -3))
    },
    1: {
        "g_id": (-10, -3),
        "grid_index": create_grid_index(geolayer_for_index, mesh_size=1),
        "nb_mesh": 2,
        "g_id_include": True,
        "return_value": ((-12, -5), (-12, -4), (-12, -3), (-11, -5), (-11, -4), (-11, -3), (-10, -5), (-10, -4),
                         (-10, -3), (-9, -5), (-9, -4), (-9, -3), (-8, -5), (-8, -4), (-8, -3))
    },
    2: {
        "g_id": (-10, -3),
        "grid_index": create_grid_index(geolayer_for_index, mesh_size=1),
        "nb_mesh": 1,
        "g_id_include": False,
        "return_value": ((-11, -4), (-11, -3), (-10, -4), (-9, -4), (-9, -3))
    },
    3: {
        "g_id": (-10, -3),
        "grid_index": create_grid_index(geolayer_for_index, mesh_size=1),
        "nb_mesh": 2,
        "g_id_include": False,
        "return_value": ((-12, -5), (-12, -4), (-12, -3), (-11, -5), (-11, -4), (-11, -3), (-10, -5), (-10, -4),
                         (-9, -5), (-9, -4), (-9, -3), (-8, -5), (-8, -4), (-8, -3))
    },
}

create_grid_index_parameters = {
    0: {
        'geolayer': geolayer_for_index,
        'mesh_size':  30,
        'x_grid_origin': 0,
        'y_grid_origin':  0,
        'return_value': geolayer_for_index_grid_index
    },
    1:  {
        'geolayer': geolayer_for_index_width,
        'mesh_size':  30,
        'x_grid_origin': 0,
        'y_grid_origin':  0,
        'return_value': geolayer_for_index_width_grid_index
    },
    2: {
        'geolayer': geolayer_for_index_height,
        'mesh_size': 30,
        'x_grid_origin': 0,
        'y_grid_origin': 0,
        'return_value': geolayer_for_index_height_grid_index
    },
    3:  {
        'geolayer': geolayer_for_index_width_height,
        'mesh_size':  30,
        'x_grid_origin': 0,
        'y_grid_origin':  0,
        'return_value': geolayer_for_index_width_height_grid_index
    },
}

grid_index_to_geolayer_parameters = {
    0: {
        "grid_index": geolayer_for_index_grid_index,
        "name": 'grid_index',
        "crs": None,
        "features_serialize": False,
        "return_value": geolayer_for_index_grid_geolayer
    },
    1: {
        "grid_index": geolayer_for_index_width_grid_index,
        "name": 'grid_index',
        "crs": None,
        "features_serialize": False,
        "return_value": geolayer_for_index_width_grid_geolayer
    },
    2: {
        "grid_index": geolayer_for_index_height_grid_index,
        "name": 'grid_index',
        "crs": None,
        "features_serialize": False,
        "return_value": geolayer_for_index_height_grid_geolayer
    },
    3: {
        "grid_index": geolayer_for_index_width_height_grid_index,
        "name": 'grid_index',
        "crs": None,
        "features_serialize": False,
        "return_value": geolayer_for_index_width_height_grid_geolayer
    }
}


def test_alea_point_to_g_id_to_bbox(nb_iteration):
    cnt_loop = 0
    bbox = (-100, -100, 100, 100)
    nb_round = 2
    for i in range(nb_iteration):
        test_point = random_point(bbox=bbox, nb_round=nb_round)
        mesh_size = round(random.random() * 10, 2)
        # print(test_point, mesh_size)
        if mesh_size < 1:
            mesh_size = 1
        for g_id in point_to_g_id(test_point, mesh_size):
            test_bbox = g_id_to_bbox(g_id, mesh_size, grid_precision=nb_round + 1)
            cnt_loop += 1
            if not point_intersects_bbox(test_point, test_bbox):
                print(test_point, mesh_size)
                return False
    print('\tnb g_id tested', cnt_loop)
    return True


def test_alea_segment_to_g_id_to_bbox(nb_iteration):
    bbox = (-100, -100, 100, 100)
    cnt_loop = 0
    nb_round = 2
    for i in range(nb_iteration):
        segment = random_segment(bbox=bbox, nb_round=nb_round)
        mesh_size = round(random.random() * 100, 2)
        # print(test_point, mesh_size)
        if mesh_size < 1:
            mesh_size = 1.
        segment_bbox = segment_to_bbox(segment)
        for g_id in bbox_to_g_id(segment_bbox, mesh_size):
            test_bbox = g_id_to_bbox(g_id, mesh_size, grid_precision=nb_round + 1)
            cnt_loop += 1
            if not bbox_intersects_bbox(segment_bbox, test_bbox):
                print(segment, segment_bbox, test_bbox, g_id, mesh_size)
                return False
    print('\tnb g_id tested', cnt_loop)
    return True


def test_alea_bbox_to_g_id_to_bbox(nb_iteration):
    bbox = (-100, -100, 100, 100)
    cnt_loop = 0
    nb_round = 2
    for i in range(nb_iteration):
        test_bbox_a = random_bbox(bbox=bbox, nb_round=nb_round)
        mesh_size = round(random.random() * 100, 2)
        # print(test_point, mesh_size)
        if mesh_size < 1:
            mesh_size = 1.
        for g_id in bbox_to_g_id(test_bbox_a, mesh_size):
            test_bbox_b = g_id_to_bbox(g_id, mesh_size, grid_precision=nb_round + 1)
            cnt_loop += 1
            if not bbox_intersects_bbox(test_bbox_a, test_bbox_b):
                print(test_bbox_a, test_bbox_b, g_id, mesh_size)
                return False
    print('\tnb g_id tested', cnt_loop)
    return True


def test_all():
    # bbox_to_g_id
    print(test_function(bbox_to_g_id, bbox_to_g_id_parameters))

    # point_to_g_id
    print(test_function(point_to_g_id, point_to_g_id_parameters))

    # g_id_to_bbox
    print(test_function(g_id_to_bbox, g_id_to_bbox_parameters))

    # g_id_to_point
    print(test_function(g_id_to_point, g_id_to_point_parameters))

    # g_id_neighbor_in_grid_index
    print(test_function(g_id_neighbor_in_grid_index, g_id_neighbor_in_grid_index_parameters))

    #  create_grid_index
    print(test_function(create_grid_index, create_grid_index_parameters))

    # grid_index_to_geolayer
    print(test_function(grid_index_to_geolayer, grid_index_to_geolayer_parameters))


    iteration = 1000000
    alea_point_to_g_id_to_bbox = test_alea_point_to_g_id_to_bbox(nb_iteration=iteration)
    if alea_point_to_g_id_to_bbox:
        print('Func test point_to_g_id / g_id_to_bbox / point_intersect_bbox OK')
    else:
        print('Func test point_to_g_id / g_id_to_bbox / point_intersect_bbox NOK')

    iteration = 10000
    alea_bbox_to_g_id_to_bbox = test_alea_segment_to_g_id_to_bbox(nb_iteration=iteration)
    if alea_bbox_to_g_id_to_bbox:
        print('Func test segment_to_bbox / bbox_to_g_id / g_id_to_bbox / bbox_intersects_bbox OK')
    else:
        print('Func segment_to_bbox/ test bbox_to_g_id / g_id_to_bbox / bbox_intersects_bbox NOK')


    iteration = 10000
    alea_bbox_to_g_id_to_bbox = test_alea_bbox_to_g_id_to_bbox(nb_iteration=iteration)
    if alea_bbox_to_g_id_to_bbox:
        print('Func test bbox_to_g_id / g_id_to_bbox / bbox_intersects_bbox OK')
    else:
        print('Func test bbox_to_g_id / g_id_to_bbox / bbox_intersects_bbox NOK')


if __name__ == '__main__':
    test_all()
