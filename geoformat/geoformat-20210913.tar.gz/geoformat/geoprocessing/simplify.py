from geoformat.geoprocessing.generalization.ramer_douglas_peucker import ramer_douglas_peucker
from geoformat.geoprocessing.generalization.visvalingam_whyatt import visvalingam_whyatt
from geoformat.conversion.geometry_conversion import geometry_to_geometry_collection, multi_geometry_to_single_geometry


def simplify(geometry, tolerance, algo='RDP'):
    """
    Generalize input geometry to a given tolerance with a specified generalization algorithm.

    algorithm list :
        RDP : Ramer Douglas Peucker
        VW : Visvalingam Whyatt

    Compare Rameer Douglas Peucker and Visvalingam Whyatt :
        http://bl.ocks.org/msbarry/9152218
        https://martinfleischmann.net/line-simplification-algorithms/

    To visually test the algorithms one can use: https://mapshaper.org/

    :param geometry: geometry to generalize.
    :param tolerance: tolerance threshold for generalization.
    :param algo: type of algorithm used to make the generalisation (two values allowed RDP or VW).
    :return: generalized geometry
    """

    # init algo
    if algo == 'RDP':
        simplify_algorithm = ramer_douglas_peucker
    elif algo == 'VW':
        simplify_algorithm = visvalingam_whyatt
    else:
        raise Exception(
            "You have to choose between two values : 'RDP' (Ramer Douglas Peucker) or 'VW' (Visvalingam Whyatt")

    input_geometry_type = geometry["type"]
    # transform geometry in geometry_collection collection
    geometry_collection = geometry_to_geometry_collection(geometry=geometry, bbox=False)
    result_geometry_collection = {"type": 'GeometryCollection', "geometries": []}
    # loop on each geometries
    for geometry_in_collection in geometry_collection['geometries']:
        in_collection_geometry_coordinates = []
        # if geometry_collection is a multi geometry_collection loop on each single geometry_collection
        for single_geometry in multi_geometry_to_single_geometry(geometry_in_collection, bbox=False):
            # if single geometry_collection is LineString or Polygon we can simplify it
            if single_geometry['type'] in {"LineString", "Polygon"}:
                # create a basic coordinates list to launch ramer douglas peucker in it
                coordinates_list = single_geometry['coordinates']
                if single_geometry['type'] == 'LineString':
                    coordinates_list = [single_geometry['coordinates']]
                # loop on each coordinates
                result_coordinates_list = []
                for coordinates_list in coordinates_list:
                    result_coordinates = (simplify_algorithm(coordinate_list=coordinates_list, tolerance=tolerance))
                    result_coordinates_list.append(result_coordinates)

                if single_geometry['type'] == 'LineString':
                    result_coordinates_list = result_coordinates_list[0]

            # if single_geometry is point (we do nothing)
            else:
                result_coordinates_list = single_geometry['coordinates']

            in_collection_geometry_coordinates.append(result_coordinates_list)

        if 'Multi' not in geometry_in_collection['type']:
            in_collection_geometry_coordinates = in_collection_geometry_coordinates[0]

        result_geometry_in_collection = {
            "type": str(geometry_in_collection['type']),
            "coordinates": in_collection_geometry_coordinates
        }
        result_geometry_collection['geometries'].append(result_geometry_in_collection)

    # if input geometry is not GeometryCollection we return geometry's original type
    if input_geometry_type != 'GeometryCollection':
        output_geometry = result_geometry_collection['geometries'][0]
    else:
        output_geometry = result_geometry_collection

    return output_geometry


