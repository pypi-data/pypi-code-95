

def envelope_to_bbox(envelope):
    """
    Convert envelope to bbox
        FYI :
            envelope format (x_min, x_max, y_min, y_max)
            bbox format (x_min, y_min, x_max, y_max)

    :param envelope: input envelope
    :return: (x_min, y_min, x_max, y_max)
    """

    return envelope[0], envelope[2], envelope[1], envelope[3]


def bbox_to_envelope(bbox):
    """
    Convert bbox to envelope
        FYI :
            envelope format (x_min, x_max, y_min, y_max)
            bbox format (x_min, y_min, x_max, y_max)

    :param bbox: input bbox
    :return: (x_min, x_max, y_min, y_max)
    """

    return bbox[0], bbox[2], bbox[1], bbox[3]


def bbox_extent_to_2d_bbox_extent(bbox_extent):
    """
    Convert a bbox or extent with 2 or more dimension to 2d extent

    :param bbox_extent:  bbox or extent with 2d or more dimension
    :return:  new bbox or extent with only 2 dimensions
    """
    mid_idx = int(len(bbox_extent) / 2)
    bbox = (bbox_extent[0], bbox_extent[1], bbox_extent[mid_idx], bbox_extent[mid_idx + 1])

    return bbox


def bbox_to_polygon_coordinates(bbox):
    """
    This function send polygon coordinates from a gives bbox

    :param bbox: input bbox
    :return: polygon coordinates
    """
    (x_min, y_min, x_max, y_max) = bbox

    return [[[x_min, y_min], [x_min, y_max], [x_max, y_max], [x_max, y_min], [x_min, y_min]]]