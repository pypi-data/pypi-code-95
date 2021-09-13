from geoformat.geoprocessing.connectors.predicates import (
    point_intersects_point,
    point_intersects_segment,
    point_intersects_bbox,
    segment_intersects_segment,
    segment_intersects_bbox,
    bbox_intersects_bbox,
    ccw_or_cw_segments,
    point_position_segment
)

from test_all import test_function

point_intersects_point_parameters = {
    0: {
        'point_a': (10, 10),
        'point_b': (10, 10),
        'tolerance': None,
        'return_value': True
    },
    1: {
        'point_a': (-5, 5),
        'point_b': (5, -5),
        'tolerance': None,
        'return_value': False
    },
    3: {
        'point_a': (10, 10),
        'point_b': (10, 10),
        'tolerance': 0.0,
        'return_value': True
    },
    4: {
        'point_a': (-5, 5),
        'point_b': (5, -5),
        'tolerance': 0.,
        'return_value': False
    },
    5: {
        'point_a': (10.1, 10.),
        'point_b': (10, 10),
        'tolerance': 0.1,
        'return_value': True
    },
    6: {
        'point_a': (-5, 5),
        'point_b': (5, -5),
        'tolerance': 0.1,
        'return_value': False
    },
    7: {
        'point_a': (10.1, 10.),
        'point_b': (10, 10),
        'tolerance': 0.01,
        'return_value': False
    },
    8: {
        'point_a': (-5, 5),
        'point_b': (5, -5),
        'tolerance': 15,
        'return_value': True
    },
}

point_intersects_segment_parameters = {
    0: {
        'point': (0, 0),
        'segment': ((-10, -10), (10, 10)),
        'tolerance': None,
        'return_value': True
    },
    1: {
        'point': (-11, -11),
        'segment': ((-10, -10), (10, 10)),
        'tolerance': None,
        'return_value': False
    },
    2: {
        'point': (2, 2),
        'segment': ((1, 2), (3, 2)),
        'tolerance': None,
        'return_value': True
    },
    3: {
        'point': (1.9, 1.9),
        'segment': ((1, 2), (3, 2)),
        'tolerance': None,
        'return_value': False
    },
    4: {
        'point': (1.9, 1.9),  # point near the middle of segment
        'segment': ((1, 2), (3, 2)),  # horizontal segment
        'tolerance': 0.1,
        'return_value': True
    },
    5: {
        'point': (1.9, 1.9),  # point near the middle of segment
        'segment': ((1, 2), (3, 2)),  # horizontal segment
        'tolerance': 0.01,
        'return_value': False
    },
    6: {
        'point': (1.99, 1.99),  # point near the middle of segment
        'segment': ((1, 2), (3, 2)),  # horizontal segment
        'tolerance': 0.01,
        'return_value': True
    },
    7: {
        'point': (0.9, 1.9),  # point near the beginning of segment
        'segment': ((1, 2), (3, 2)),  # horizontal segment
        'tolerance': 0.1,
        'return_value': True
    },
    8: {
        'point': (0.9, 1.9),  # point near the beginning of segment
        'segment': ((1, 2), (3, 2)),  # horizontal segment
        'tolerance': 0.01,
        'return_value': False
    },
    9: {
        'point': (0.99, 1.99),  # point near the beginning of segment
        'segment': ((1, 2), (3, 2)),  # horizontal segment
        'tolerance': 0.01,
        'return_value': True
    },
    10: {
        'point': (3.1, 2.1),  # point near the ending of segment
        'segment': ((1, 2), (3, 2)),  # horizontal segment
        'tolerance': 0.1,
        'return_value': True
    },
    11: {
        'point': (3.1, 2.1),  # point near the ending of segment
        'segment': ((1, 2), (3, 2)),  # horizontal segment
        'tolerance': 0.01,
        'return_value': False
    },
    12: {
        'point': (3.01, 2.01),  # point near the ending of segment
        'segment': ((1, 2), (3, 2)),  # horizontal segment
        'tolerance': 0.01,
        'return_value': True
    },
    13: {
        'point': (-2.1, -1.9),  # point near the middle of segment
        'segment': ((-2, -1), (-2, -3)),  # vertical segment
        'tolerance': 0.1,
        'return_value': True
    },
    14: {
        'point': (-2.1, -1.9),  # point near the middle of segment
        'segment': ((-2, -1), (-2, -3)),  # vertical segment
        'tolerance': 0.01,
        'return_value': False
    },
    15: {
        'point': (-2.01, -1.09),  # point near the middle of segment
        'segment': ((-2, -1), (-2, -3)),  # vertical segment
        'tolerance': 0.01,
        'return_value': True
    },
    16: {
        'point': (-1.9, -0.9),  # point near at the segment beginning
        'segment': ((-2, -1), (-2, -3)),  # vertical segment
        'tolerance': 0.1,
        'return_value': True
    },
    17: {
        'point': (-1.9, -0.9),  # point near at the segment beginning
        'segment': ((-2, -1), (-2, -3)),  # vertical segment
        'tolerance': 0.01,
        'return_value': False
    },
    18: {
        'point': (-1.99, -0.99),  # point near at the segment beginning
        'segment': ((-2, -1), (-2, -3)),  # vertical segment
        'tolerance': 0.01,
        'return_value': True
    },
    19: {
        'point': (-2.1, -2.9),  # point near at the segment ending
        'segment': ((-2, -1), (-2, -3)),  # vertical segment
        'tolerance': 0.1,
        'return_value': True
    },
    20: {
        'point': (-2.1, -2.9),  # point near at the segment ending
        'segment': ((-2, -1), (-2, -3)),  # vertical segment
        'tolerance': 0.01,
        'return_value': False
    },
    21: {
        'point': (-2.01, -2.99),  # point near at the segment ending
        'segment': ((-2, -1), (-2, -3)),  # vertical segment
        'tolerance': 0.01,
        'return_value': True
    },
    22: {
        'point': (-0.1, 4),  # point near the middle of segment
        'segment': ((-1, 3), (1, 5)),
        'tolerance': 0.1,
        'return_value': True
    },
    23: {
        'point': (-0.1, 4),  # point near the middle of segment
        'segment': ((-1, 3), (1, 5)),
        'tolerance': 0.01,
        'return_value': False
    },
    24: {
        'point': (-0.01, 4),  # point near the middle of segment
        'segment': ((-1, 3), (1, 5)),
        'tolerance': 0.01,
        'return_value': True
    },
    25: {
        'point': (1.99999, 2.00001),
        'segment': ((1, 1), (3, 3)),
        'tolerance': 0.0001,
        'return_value': True
    },
    26: {
        'point': (1.99999, 2.00001),
        'segment': ((1, 1), (3, 3)),
        'tolerance': 0.00001,
        'return_value': True
    },
    27: {
        'point': (2, 2.00001),
        'segment': ((1, 1), (3, 3)),
        'tolerance': 0.00001,
        'return_value': True
    },
    28: {
        'point': [645301, 6779557.0331],
        'segment': [[645285, 6779558], [647006, 6779454]],
        'tolerance': 0.00001,
        'return_value': False
    },
    29: {
        'point': [645301, 6779557.03312],
        'segment': [[645285, 6779558], [647006, 6779454]],
        'tolerance': 0.0000001,
        'return_value': False
    },
    30: {
        'point': [645301, 6779557.03312],
        'segment': [[645285, 6779558], [647006, 6779454]],
        'tolerance': 0.000001,
        'return_value': True
    },
    31: {
        'point': [645301, 6779557.03312],
        'segment': [[645285, 6779558], [647006, 6779454]],
        'tolerance': None,
        'return_value': False
    },
    32: {
        'point': [645301, 6779557.03312],
        'segment': [[645285, 6779558], [647006, 6779454]],
        'tolerance': 0.0000001,
        'return_value': False
    },
    33: {
        'point': [645301, 6779557.03312],
        'segment': [[645285, 6779558], [647006, 6779454]],
        'tolerance': 0.000001,
        'return_value': True
    },
    34: {
        "point": (2, 2.05),
        "segment": ((1.95, 2), (2.05, 2)),  # segment length < tolerance
        "tolerance": 0.05,
        "return_value": True
    },
    35: {
        "point": (2, 2.05),
        "segment": ((1.99, 2), (2.01, 2)),
        "tolerance": 0.05,
        "return_value": True
    },
    36: {
        "point": (-10, -5),
        "segment": ([-10, -10], [-10, 10]),
        "tolerance": 1,
        "return_value": True
    },
    37: {
        'point': (0, 0),
        'segment': ((-10, -10), (10, 10)),
        "tolerance": None,
        'return_value': True
    },
    38: {
        'point': (10, 10),
        'segment': ((-10, -10), (10, 10)),
        "tolerance": None,
        'return_value': True
    },
    39: {
        'point': (-10, -10),
        'segment': ((-10, -10), (10, 10)),
        "tolerance": None,
        'return_value': True
    },
    40: {
        'point': (-11, -11),
        'segment': ((-10, -10), (10, 10)),
        "tolerance": None,
        'return_value': False
    },
}


point_intersects_bbox_parameters = {
    0: {
        'point': (0, 0),
        'bbox': (-10, -10, 10, 10),
        'return_value': True
    },
    1: {
        'point': (-10, -10),
        'bbox': (-10, -10, 10, 10),
        'return_value': True
    },
    2: {
        'point': (-10, 10),
        'bbox': (-10, -10, 10, 10),
        'return_value': True
    },
    3: {
        'point': (10, 10),
        'bbox': (-10, -10, 10, 10),
        'return_value': True
    },
    4: {
        'point': (10, -10),
        'bbox': (-10, -10, 10, 10),
        'return_value': True
    },
    5: {
        'point': (-10, 0),
        'bbox': (-10, -10, 10, 10),
        'return_value': True
    },
    6: {
        'point': (0, 10),
        'bbox': (-10, -10, 10, 10),
        'return_value': True
    },
    7: {
        'point': (10, 0),
        'bbox': (-10, -10, 10, 10),
        'return_value': True
    },
    8: {
        'point': (0, -10),
        'bbox': (-10, -10, 10, 10),
        'return_value': True
    },
    9: {
        'point': (-10, -20),
        'bbox': (-10, -10, 10, 10),
        'return_value': False
    }
}

segment_intersects_segment_parameters = {
    0: {
        'segment_a': ((10, 10), (-10, -10)),
        'segment_b': ((-10, 10), (10, -10)),
        'return_value': True
    },
    1: {
        'segment_a': ((10, 10), (-10, -10)),
        'segment_b': ((0, 10), (20, 10)),
        'return_value': True
    },
    2: {
        'segment_a': ((10, 10), (-10, -10)),
        'segment_b': ((-10, -10), (0, -10)),
        'return_value': True
    },
    3: {
        'segment_a': ((10, 10), (-10, -10)),
        'segment_b': ((10, 10), (20, 20)),
        'return_value': True
    },
    4: {
        'segment_a': ((10, 10), (-10, -10)),
        'segment_b': ((-10, -10), (-20, -20)),
        'return_value': True
    },
    5: {
        'segment_a': ((10, 10), (-10, -10)),
        'segment_b': ((3, 0), (5, -2)),
        'return_value': False
    },
}

segment_intersects_bbox_parameters = {
    0: {
        'segment': ((-2, 0), (2, 0)),
        'bbox': (-10, -10, 10, 10),
        'return_value': True
    },
    1: {
        'segment': ((-5, -10), (5, -10)),
        'bbox': (-10, -10, 10, 10),
        'return_value': True
    },
    2: {
        'segment': ((-10, -20), (-10, 20)),
        'bbox': (-10, -10, 10, 10),
        'return_value': True
    },
    3: {
        'segment': ((5, 10), (-20, 10)),
        'bbox': (-10, -10, 10, 10),
        'return_value': True
    },
    4: {
        'segment': ((10, 5), (10, 30)),
        'bbox': (-10, -10, 10, 10),
        'return_value': True
    },
    5: {
        'segment': ((-9, 11), (-11, 9)),
        'bbox': (-10, -10, 10, 10),
        'return_value': True
    },
    6: {
        'segment': ((-10, -10), (-20, -10)),
        'bbox': (-10, -10, 10, 10),
        'return_value': True
    },
    7: {
        'segment': ((11, -9), (9, 11)),
        'bbox': (-10, -10, 10, 10),
        'return_value': True
    },
    8: {
        'segment': ((10, 30), (10, 10)),
        'bbox': (-10, -10, 10, 10),
        'return_value': True
    },
    9: {
        'segment': ((20, 5), (30, 5)),
        'bbox': (-10, -10, 10, 10),
        'return_value': False
    },
    10: {
        'segment': ([-62136.394556539126, 5596571.563702659], [-60626.17017134098, 5597872.545653571]),
        'bbox': (-61500.0, 5597250.0, -61450.0, 5597300.0),
        'return_value': False
    }
}

bbox_intersects_bbox_parameters = {
    0: {
        'bbox_a': (-10, -10, 10, 10),
        'bbox_b': (-10, -10, 10, 10),
        'return_value': True
    },
    1: {
        'bbox_a': (-10, -10, 10, 10),
        'bbox_b': (-20, -20, 0, 0),
        'return_value': True
    },
    2: {
        'bbox_a': (-10, -10, 10, 10),
        'bbox_b': (-20, -20, 0, 0),
        'return_value': True
    },
    3: {
        'bbox_a': (-10, -10, 10, 10),
        'bbox_b': (-30, -30, -10, 0),
        'return_value': True
    },
    4: {
        'bbox_a': (-10, -10, 10, 10),
        'bbox_b': (11, 11, 40, 40),
        'return_value': False
    }
}

ccw_or_cw_segments_parameters = {
    0: {
        'segment_a': ((-5, -5), (5, 5)),
        'segment_b':  ((5, 5), (-1, 2)),
        'return_value': 'CCW'
    },
    1: {
        'segment_a': ((-5, -5), (5, 5)),
        'segment_b': ((5, 5), (5, -5)),
        'return_value': 'CW'
    },
    2: {
        'segment_a': ((-5, -5), (5, 5)),
        'segment_b': ((5, 5), (10, 10)),
        'return_value': 'NEITHER'
    },
    3: {
        'segment_a': ((-5, -5), (5, 5)),
        'segment_b': ((4, 4), (10, 10)),
        'return_value': None
    },
    4: {
        'segment_a': ((5, 5), (-5, -5)),
        'segment_b': ((-5, -5), (-1, 2)),
        'return_value': 'CW'
    },
    5: {
        'segment_a': ((5, 5), (-5, -5)),
        'segment_b': ((-5, -5), (5, -5)),
        'return_value': 'CCW'
    },
    6: {
        'segment_a': ((5, 5), (-5, -5)),
        'segment_b': ((-5, -5), (10, 10)),
        'return_value': 'NEITHER'
    },
    7: {
        'segment_a':  ((5, 5), (-5, -5)),
        'segment_b':  ((-4, -4), (10, 10)),
        'return_value': None
    },
}

point_position_segment_parameters = {
    0: {
        'segment': ((-5, -5), (5, 5)),
        'point':  (-1, 2),
        'return_value': 'LEFT'
    },
    1: {
        'segment': ((-5, -5), (5, 5)),
        'point':  (5, -5),
        'return_value': 'RIGHT'
    },
    2: {
        'segment': ((-5, -5), (5, 5)),
        'point': (10, 10),
        'return_value': 'NEITHER'
    },
    3: {
        'segment': ((-5, -5), (5, 5)),
        'point': (0, 0),
        'return_value': 'ON'
    },
    4: {
        'segment': ((5, 5), (-5, -5)),
        'point': (-1, 2),
        'return_value': 'RIGHT'
    },
    5: {
        'segment': ((5, 5), (-5, -5)),
        'point': (5, -5),
        'return_value': 'LEFT'
    },
    6: {
        'segment': ((5, 5), (-5, -5)),
        'point': (10, 10),
        'return_value': 'NEITHER'
    },
    7: {
        'segment': ((5, 5), (-5, -5)),
        'point': (0, 0),
        'return_value': 'ON'
    }
}


def test_all():
    # point_intersects_point
    print(test_function(point_intersects_point, point_intersects_point_parameters))

    # point_intersects_segment
    print(test_function(point_intersects_segment, point_intersects_segment_parameters))

    # point_intersects_bbox
    print(test_function(point_intersects_bbox, point_intersects_bbox_parameters))

    # segment_intersects_segment
    print(test_function(segment_intersects_segment, segment_intersects_segment_parameters))

    # segment_intersects_bbox
    print(test_function(segment_intersects_bbox, segment_intersects_bbox_parameters))

    # bbox_intersects_bbox
    print(test_function(bbox_intersects_bbox, bbox_intersects_bbox_parameters))

    # ccw_or_cw_segments
    print(test_function(ccw_or_cw_segments, ccw_or_cw_segments_parameters))

    # point_position_segment
    print(test_function(point_position_segment, point_position_segment_parameters))


if __name__ == '__main__':
    test_all()
