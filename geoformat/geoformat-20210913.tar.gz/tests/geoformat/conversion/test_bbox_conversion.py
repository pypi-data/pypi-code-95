from geoformat.conversion.bbox_conversion import (
    envelope_to_bbox,
    bbox_to_envelope,
    bbox_extent_to_2d_bbox_extent,
    bbox_to_polygon_coordinates
)

from test_all import test_function

envelope_to_bbox_parameters = {
    0: {
        "envelope": (-10, 10, -10, 10),
        "return_value": (-10, -10, 10, 10)
    },
    1: {
        "envelope": (0, 10, 0, 10),
        "return_value": (0, 0, 10, 10)
    },
    2: {
        "envelope": (-10, 0, -10,  0),
        "return_value": (-10, -10, 0, 0)
    },
    3: {
        "envelope": (-10, -10, 10, 10),
        "return_value": (-10, 10, -10, 10)
    },
    4: {
        "envelope": (0, 0, 10, 10),
        "return_value":  (0, 10, 0, 10)
    },
    5: {
        "envelope": (-10, -10, 0, 0),
        "return_value": (-10, 0, -10, 0)
    }
}

bbox_to_envelope_parameters = {
    0: {
        "bbox": (-10, 10, -10, 10),
        "return_value": (-10, -10, 10, 10)
    },
    1: {
        "bbox": (0, 10, 0, 10),
        "return_value": (0, 0, 10, 10)
    },
    2: {
        "bbox": (-10, 0, -10, 0),
        "return_value": (-10, -10, 0, 0)
    },
    3: {
        "bbox": (-10, -10, 10, 10),
        "return_value": (-10, 10, -10, 10)
    },
    4: {
        "bbox": (0, 0, 10, 10),
        "return_value":  (0, 10, 0, 10)
    },
    5: {
        "bbox": (-10, -10, 0, 0),
        "return_value": (-10, 0, -10, 0)
    }
}

bbox_extent_to_2d_bbox_extent_parameters = {
    0: {
        "bbox_extent": (-10, -10, -10, 10, 10, 10),
        "return_value":  (-10, -10, 10, 10)
    },
    1:  {
        "bbox_extent": (-10, -10, -10, 10, 10, 10, 10, 10),
        "return_value":  (-10, -10, 10, 10)
    },
}

bbox_to_polygon_coordinates_parameters = {
    0: {
        'bbox': (-10, -10, 10, 10),
        'return_value': [[[-10, -10], [-10, 10],  [10, 10], [10, -10], [-10, -10]]]
    },
}

def test_all():
    # bbox_to_envelope
    print(test_function(bbox_to_envelope, bbox_to_envelope_parameters))

    # envelope_to_bbox
    print(test_function(envelope_to_bbox, envelope_to_bbox_parameters))

    # bbox_extent_to_2d_bbox_extent
    print(test_function(bbox_extent_to_2d_bbox_extent, bbox_extent_to_2d_bbox_extent_parameters))

    # bbox_to_polygon_coordinates
    print(test_function(bbox_to_polygon_coordinates, bbox_to_polygon_coordinates_parameters))


if __name__ == '__main__':
    test_all()