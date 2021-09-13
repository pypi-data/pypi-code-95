from geoformat.geoprocessing.connectors.operations import (
    coordinates_to_point,
    coordinates_to_segment
)
from geoformat.geoprocessing.connectors.predicates import (
    point_intersects_point,
    point_intersects_segment
)

from geoformat.conversion.geometry_conversion import (
    single_geometry_to_multi_geometry,
    multi_geometry_to_single_geometry
)
from geoformat.conversion.segment_conversion import (
    segment_list_to_linestring
)

from geoformat.geoprocessing.geoparameters.bbox import bbox_union


def segment_split_by_point(segment, point, tolerance=None):
    """
    This function return a generator with split segments if point intersects it. If not the full segment is yield

    :param segment: segment that you want split with a point.
    :param point: point that will split segment.
    :param tolerance: distance below which two geographic objects are considered to be confused.
    :return: generator with split segment.
    """
    # if point intersects segment
    if point_intersects_segment(point, segment, tolerance):
        point_begin_segment = segment[0]
        point_end_segment = segment[1]
        # print(point_intersects_point(point, point_begin_segment, tolerance) )
        # test if point is not at segment extremity
        if not point_intersects_point(point, point_begin_segment, tolerance) \
                and not point_intersects_point(point, point_end_segment, tolerance):
            segment_a = point_begin_segment, point
            segment_b = point, point_end_segment
            yield segment_a
            yield segment_b


def linestring_split_by_point(linestring, point, tolerance=None, bbox=True):
    # TODO 1/ add tolerance consideration [DONE]
    # TODO 2/ delete duplicate points (if exists)
    # TODO 3/ optimize filter point intersection bbox_linestring
    # TODO 4/ optimize with segment that intersects points (grid index ?)
    # TODO 5/ manage bbox [DONE]
    # ToDO 6/ if output same that output => return geometry collection ?

    # transform point and linestring to multipoint and multilinestring
    multilinestring = single_geometry_to_multi_geometry(linestring)
    multi_point = single_geometry_to_multi_geometry(point)
    for _point in coordinates_to_point(multi_point['coordinates']):
        segment_split_list = []
        for _linestring in multi_geometry_to_single_geometry(multilinestring):
            # create a separation for new linestring
            segment_split_list.append([])
            # loop on each linestring segments
            for segment in coordinates_to_segment(_linestring['coordinates']):
                if point_intersects_segment(point=_point, segment=segment, tolerance=tolerance):
                    # point to cut can be :
                    #   1. on segment (we split the segment and create a cutting separation in segment_split_list )
                    #   2. at extremity point of segment (segment is preserve but a cutting separation must be done with
                    #   next segment)
                    point_at_extremity = True
                    for i_split, segment_split in enumerate(segment_split_by_point(segment=segment, point=_point, tolerance=tolerance)):
                        # if return split segment we validate condition 1.
                        point_at_extremity = False
                        segment_split_list[-1].append(segment_split)
                        if i_split == 0:
                            segment_split_list.append([])
                    # if point_at_extremity we validate condition 2.
                    if point_at_extremity is True:
                        # test if there is data in segment_split_list
                        if segment_split_list[-1]:
                            # if first point to segment is equal to last point to last segment in segment_split_list
                            # we create a new split
                            if point_intersects_point(_point, segment[0], tolerance) and segment[0] == segment_split_list[-1][-1][1]:
                                segment_split_list.append([])
                        segment_split_list[-1].append(segment)
                else:
                    segment_split_list[-1].append(segment)

        # rebuild new multilinestring with cut linestring
        multilinestring = {'type': 'MultiLinestring', 'coordinates': []}
        for segment_list in segment_split_list:
            __linestring = segment_list_to_linestring(segment_list, bbox=False, segment_as_part=False)
            multilinestring['coordinates'].append(__linestring['coordinates'])

    # prepare return
    geometries_to_return = []
    # if bbox is True
    if bbox is True:
        collection_bbox = ()
    for ___linestring in multi_geometry_to_single_geometry(multilinestring, bbox=bbox):
        if bbox is True and 'bbox' in ___linestring:
            if collection_bbox:
                collection_bbox = bbox_union(collection_bbox, ___linestring['bbox'])
            else:
                collection_bbox = ___linestring['bbox']
        geometries_to_return.append(___linestring)

    output_geometry = {'type': 'GeometryCollection', 'geometries': geometries_to_return}

    if bbox is True:
        output_geometry["bbox"] = collection_bbox

    return output_geometry
