from geoformat.geoprocessing.union import union_by_split

from tests.data.geometries import (
    test_polygon_a,
    test_polygon_b,
    test_polygon_c
)

from test_all import (
    test_function,
    test_dependencies
)

union_by_split_parameters = {
    0: {
        "geometry_list": [test_polygon_a, test_polygon_b],
        "split_factor": 2,
        "bbox": False,
        "return_value": {'type': 'Polygon', 'coordinates': [[[-2.0, 2.0], [2.0, 2.0], [2.0, 1.0], [3.0, 1.0], [3.0, -3.0], [-1.0, -3.0], [-1.0, -2.0], [-2.0, -2.0], [-2.0, 2.0]]]}
    },
    1: {
        "geometry_list": [test_polygon_a, test_polygon_b],
        "split_factor": 4,
        "bbox": False,
        "return_value": {'type': 'Polygon', 'coordinates': [[[-2.0, 2.0], [2.0, 2.0], [2.0, 1.0], [3.0, 1.0], [3.0, -3.0], [-1.0, -3.0], [-1.0, -2.0], [-2.0, -2.0], [-2.0, 2.0]]]}
    },
    2: {
        "geometry_list": [test_polygon_a, test_polygon_c],
        "split_factor": 4,
        "bbox": False,
        "return_value":  {'type': 'MultiPolygon', 'coordinates': [[[[-2.0, 2.0], [2.0, 2.0], [2.0, -2.0], [-2.0, -2.0], [-2.0, 2.0]]], [[[2.0, 4.0], [4.0, 4.0], [4.0, 2.0], [2.0, 2.0], [2.0, 4.0]]]]}
    }
}


def test_all():

    if test_dependencies()['ogr']:
        # union_by_split
        print(test_function(union_by_split, union_by_split_parameters))


if __name__ == '__main__':
    test_all()
