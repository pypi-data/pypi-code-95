from geoformat.geoprocessing.connectors.operations import coordinates_to_bbox


def segment_list_to_linestring(segment_list, bbox=True, segment_as_part=False):
    """
    Create a linestring from a list of segment.

    :param segment_list: list that contains segment(s) in it
    :param bbox: True if we want bbox
    :param segment_as_part:
                        True : each segment are treated as a part.
                        False : all segments are considered to be part of the same line (duplicate coordinates are
                        removed).
    :return: linestring or multi linestring
    """

    if segment_as_part and len(segment_list) > 1:
        linestring = {'type': 'MultiLineString', 'coordinates': segment_list}
    else:
        linestring = {'type': 'LineString', 'coordinates': []}

        linestring_coordinates = [None] * len(segment_list) * 2
        duplicate_coordinates_list = []
        for i_seg, segment in enumerate(segment_list):
            idx = i_seg * 2
            linestring_coordinates[idx] = segment[0]
            linestring_coordinates[idx+1] = segment[1]
            # verify if there is duplicate coordinates
            if linestring_coordinates[idx-1] == linestring_coordinates[idx]:
                duplicate_coordinates_list.append(idx)

        if duplicate_coordinates_list:
            # format coordinates to delete duplicate coordinates
            for idx in reversed(duplicate_coordinates_list):
                del linestring_coordinates[idx]

        # add coordinates to linestring
        linestring['coordinates'] = linestring_coordinates

    if bbox is True:
        linestring['bbox'] = coordinates_to_bbox(linestring['coordinates'])

    return linestring
