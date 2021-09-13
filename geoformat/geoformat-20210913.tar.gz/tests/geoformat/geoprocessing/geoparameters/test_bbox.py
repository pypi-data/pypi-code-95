from test_all import test_function
from geoformat.geoprocessing.geoparameters.bbox import bbox_union, extent_bbox, point_bbox_position

extent_bbox_parameters = {
    0: {
        'bbox': (-1, -1, 1, 1),
        'extent': 10,
        'return_value': (-11, -11, 11, 11)
    },
    1: {
        'bbox': (-11, -11, 11, 11),
        'extent': -1,
        'return_value': (-10, -10, 10, 10)
    },
    2: {
        'bbox': (),
        'extent': 1,
        'return_value': (-1, -1, 1, 1)
    }
}


bbox_union_parameters = {
    0: {
        'bbox_a': (-10, -10, 0, 0),
        'bbox_b': (0, 0, 10, 10),
        'return_value': (-10, -10, 10, 10)
    },
    1: {
        'bbox_a': (-10, 0, 0, 10),
        'bbox_b': (0, -10, 10, 0),
        'return_value': (-10, -10, 10, 10)
    },
    2: {
        'bbox_a': (-1, -1, 1, 1),
        'bbox_b': (0, 0, 1, 1),
        'return_value': (-1, -1, 1, 1)
    },
    3: {
        'bbox_a': (-1, -1, 1, 1),
        'bbox_b': (-1, -1, 0, 0),
        'return_value': (-1, -1, 1, 1)
    },
    4: {
        'bbox_a': (-1, -1, 1, 1),
        'bbox_b': (-2, 1, 5, 2),
        'return_value': (-2, -1, 5, 2)
    },
    5: {
        'bbox_a': (-1, -1, 1, 1),
        'bbox_b': (2, -10, 10, -3),
        'return_value': (-1, -10, 10, 1)
    },
    6: {
        'bbox_a': (2, -10, 10, -3),
        'bbox_b': (-1, -1, 1, 1),
        'return_value': (-1, -10, 10, 1)
    },
    7: {
        'bbox_a': (),
        'bbox_b': (-1, -1, 1, 1),
        'return_value': (-1, -1, 1, 1)
    },
    8: {
        'bbox_a':  (2, -10, 10, -3),
        'bbox_b': (),
        'return_value': (2, -10, 10, -3)
    },
    9: {
        'bbox_a':  (),
        'bbox_b': (),
        'return_value': ()
    }
}

point_bbox_position_parameters = {
    0: {
        "point": (-10, 10),
        "bbox": (-10, -10, 10, 10),
        "return_value":  ('Boundary', 'NW')
    },
    1: {
        "point": (-10, 0),
        "bbox": (-10, -10, 10, 10),
        "return_value":  ('Boundary', 'W')
    },
    2: {
        "point": (10, 5),
        "bbox": (-10, -10, 10, 10),
        "return_value":  ('Boundary', 'E')
    },
    3: {
        "point": (0, 0),
        "bbox": (-10, -10, 10, 10),
        "return_value":  ('Interior', None)
    },
    4: {
        "point": (-11, 11),
        "bbox": (-10, -10, 10, 10),
        "return_value":  ('Exterior', 'NW')
    },
    5: {
        "point": (0, 11),
        "bbox": (-10, -10, 10, 10),
        "return_value":  ('Exterior', 'N')
    },
    6: {
        "point": (11, 11),
        "bbox": (-10, -10, 10, 10),
        "return_value":  ('Exterior', 'NE')
    },
    7: {
        "point": (11, 0),
        "bbox": (-10, -10, 10, 10),
        "return_value":  ('Exterior', 'E')
    },
    8: {
        "point": (11, -11),
        "bbox": (-10, -10, 10, 10),
        "return_value":  ('Exterior', 'SE')
    },
    9: {
        "point": (0, -11),
        "bbox": (-10, -10, 10, 10),
        "return_value":  ('Exterior', 'S')
    },
    10: {
        "point": (-11, -11),
        "bbox": (-10, -10, 10, 10),
        "return_value":  ('Exterior', 'SW')
    },
    11: {
        "point": (-11, 0),
        "bbox": (-10, -10, 10, 10),
        "return_value":  ('Exterior', 'W')
    },
}


def test_all():
    # bbox_extent
    print(test_function(extent_bbox, extent_bbox_parameters))

    # bbox_union
    print(test_function(bbox_union, bbox_union_parameters))

    # point_bbox_position
    print(test_function(point_bbox_position, point_bbox_position_parameters))


if __name__ == '__main__':
    test_all()
