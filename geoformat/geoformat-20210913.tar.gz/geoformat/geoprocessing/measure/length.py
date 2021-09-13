from geoformat.geoprocessing.measure.distance import (
    euclidean_distance,
    manhattan_distance
)

def segment_length(segment, distance_type='EUCLIDEAN'):
    """
    Calculate length of a given segment
    """
    (point_a, point_b) = segment
    if distance_type.upper() == 'EUCLIDEAN':
        return euclidean_distance(point_a, point_b)
    elif distance_type.upper() == 'MANHATTAN':
        return manhattan_distance(point_a, point_b)
    else:
        print('type of distance : {distance_type} does not exists'.format(distance_type=distance_type))
