from geoformat.conversion.segment_conversion import segment_list_to_linestring

from tests.data.segments import (
    segment_a,
    segment_b,
    segment_c,
    segment_e,
    segment_h)

from test_all import test_function


segment_list_to_linestring_parameters = {
    0: {
        "segment_list": [segment_a, segment_b],
        "bbox": False,
        "segment_as_part": False,
        "return_value": {"type": "LineString", "coordinates": [[0, 0], [0, 1], [0, 0]]}
    },
    1: {
        "segment_list": [segment_a, segment_b, segment_c],
        "bbox": False,
        "segment_as_part": False,
        "return_value":  {"type": "LineString", "coordinates": [[0, 0], [0, 1], [0, 0], [0, -1]]}
    },
    2: {
        "segment_list": [segment_a, segment_c, segment_e, segment_h],
        "bbox": False,
        "segment_as_part": False,
        "return_value": {"type": "LineString",
                         "coordinates": [[0, 0], [0, 1], [0, 0], [0, -1], [-1, -1], [1, 1], [-1, -1], [-1, 1]]}
    },
    3: {
        "segment_list": [segment_a, segment_b],
        "bbox": False,
        "segment_as_part": True,
        "return_value": {"type": "MultiLineString", "coordinates": [[[0, 0], [0, 1]], [[0, 1], [0, 0]]]}
    },
    4: {
        "segment_list": [segment_a, segment_b, segment_c],
        "bbox": False,
        "segment_as_part": True,
        "return_value": {"type": "MultiLineString",
                         "coordinates": [[[0, 0], [0, 1]], [[0, 1], [0, 0]], [[0, 0], [0, -1]]]}
    },
    5: {
        "segment_list": [segment_a, segment_c, segment_e, segment_h],
        "bbox": False,
        "segment_as_part": True,
        "return_value": {"type": "MultiLineString",
                         "coordinates": [[[0, 0], [0, 1]], [[0, 0], [0, -1]], [[-1, -1], [1, 1]], [[-1, -1], [-1, 1]]]}
    },
    6: {
        "segment_list": [segment_a, segment_c, segment_e, segment_h],
        "bbox": True,
        "segment_as_part": False,
        "return_value": {"type": "LineString",
                         "coordinates": [[0, 0], [0, 1], [0, 0], [0, -1], [-1, -1], [1, 1], [-1, -1], [-1, 1]],
                         "bbox": (-1, -1, 1, 1)}
    },
    7: {
        "segment_list": [segment_a, segment_c, segment_e, segment_h],
        "bbox": True,
        "segment_as_part": True,
        "return_value": {"type": "MultiLineString",
                         "coordinates": [[[0, 0], [0, 1]], [[0, 0], [0, -1]], [[-1, -1], [1, 1]], [[-1, -1], [-1, 1]]],
                         "bbox": (-1, -1, 1, 1)}
    },
    8: {
        "segment_list": [segment_a],
        "bbox": False,
        "segment_as_part": True,
        "return_value": {"type": "LineString",
                         "coordinates": [[0, 0], [0, 1]],
                         }
    },
    9: {
        "segment_list": [segment_a],
        "bbox": True,
        "segment_as_part": True,
        "return_value": {"type": "LineString",
                         "coordinates": [[0, 0], [0, 1]],
                         "bbox": (0, 0, 0, 1)}
    },
}


def test_all():
    # segment_list_to_linestring
    print(test_function(segment_list_to_linestring, segment_list_to_linestring_parameters))


if __name__ == '__main__':
    test_all()
