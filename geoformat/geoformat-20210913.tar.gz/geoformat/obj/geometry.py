from geoformat.geoprocessing.connectors.operations import coordinates_to_point
from geoformat.conversion.geometry_conversion import geometry_to_geometry_collection


def len_coordinates(coordinates):
    """
    Return number of coordinates on a coordinates list
    """

    coordinates_count = 0
    for point in coordinates_to_point(coordinates):
        coordinates_count += 1

    return coordinates_count


def len_coordinates_in_geometry(geometry):
    """
    Return number of coordinates on a given geometry
    """
    geometry_collection = geometry_to_geometry_collection(geometry)
    coordinates_count = 0
    for geometry in geometry_collection['geometries']:
        coordinates_count += len_coordinates(geometry['coordinates'])

    return coordinates_count
