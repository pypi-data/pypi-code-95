from geoformat.index.geometry.grid import (
    create_grid_index,
    bbox_to_g_id
)
from geoformat.conversion.geometry_conversion import geometry_to_ogr_geometry
from geoformat.geoprocessing.connectors.operations import coordinates_to_bbox

########################################################################################################################
#
# Adjacency matrix
#
########################################################################################################################


def create_adjacency_matrix(geolayer, mesh_size=None):
    """
    Creating an adjacency matrix

    * GDAL/OGR dependencie :
        Intersects
    *
    """

    matrix_dict = {}

    try:
        input_grid_idx = geolayer['metadata']['constraints']['index']['geometry']
    except:
        input_grid_idx = create_grid_index(geolayer, mesh_size=mesh_size)

    mesh_size = input_grid_idx['metadata']['mesh_size']

    # Création de la clé unique du dictionnaire de résultat (préparation du stockage des résultats)
    matrix_dict['matrix'] = {i_feat: set() for i_feat in geolayer['features']}

    for i_feat in geolayer['features']:
        feature_a = geolayer['features'][i_feat]

        # if feature is serialized
        if 'feature_serialize' in geolayer['metadata']:
            if geolayer['metadata']['feature_serialize']:
                feature_a = eval(feature_a)

        # get bbox
        try:
            feature_a_bbox = feature_a['geometry']['bbox']
        except KeyError:
            feature_a_bbox = coordinates_to_bbox(feature_a['geometry']['coordinates'])
            feature_a['geometry']['bbox'] = feature_a_bbox

        # Récupération des identifiants de mailles présent dans l'index
        g_id_list = list(bbox_to_g_id(feature_a_bbox, mesh_size))

        # Pour chaque identifiant de maille de l'index on récupère l'identifant des autres polygones voisins de l'entité
        # en cours (s'ils existent)
        neighbour_i_feat_list = []
        for g_id in g_id_list:
            # récupération de la liste des clefs primaires des entités présentes dans la maille de l'index
            neighbour_i_feat_list += input_grid_idx['index'][g_id]

        # suppression de la clef primaire du polyone en cours et d'éventuels doublons
        neighbour_i_feat_list = [value for value in set(neighbour_i_feat_list) if value != i_feat]

        # création  de la géométrie du feature A
        feature_a_ogr_geom = geometry_to_ogr_geometry(feature_a['geometry'])
        # Même procédé que précédemment pour l'objet B
        for neighbour_i_feat in neighbour_i_feat_list:
            # si le i_feat n'est pas déjà compris dans la matrice de proximité du voisin :
            #  si c'est le cas alors cela veut dire que l'on a déjà fait un test d'intersection enrte les deux
            #  géométries auparavant (car pour avoir un voisin il faut etre deux)

            if i_feat not in matrix_dict['matrix'][neighbour_i_feat]:
                feature_b = geolayer['features'][neighbour_i_feat]

                # if feature is serialized
                if 'feature_serialize' in geolayer['metadata']:
                    if geolayer['metadata']['feature_serialize']:
                        feature_b = eval(feature_b)

                feature_b_ogr_geom = geometry_to_ogr_geometry(feature_b['geometry'])

                if feature_a_ogr_geom.Intersects(feature_b_ogr_geom):
                    matrix_dict['matrix'][i_feat].add(neighbour_i_feat)
                    matrix_dict['matrix'][neighbour_i_feat].add(i_feat)

    matrix_dict['metadata'] = {'type': 'adjacency'}

    return matrix_dict


def get_area_intersecting_neighbors_i_feat(adjacency_matrix, i_feat, neighbor_set=None):
    """
    Use adjacency matrix to find all i_feat neighbor's.
        Return all geometries that intersects and intersects neihgbor

    """

    if not neighbor_set:
        neighbor_set = set([i_feat])

    # set store i_feat neighbor's
    i_feat_neighbor_set = set(adjacency_matrix['matrix'][i_feat])
    # difference result between the list of neighbors already scanned and i_feat neighbors
    # Anyway, it's the list of new neighbors we haven't scanned yet.
    new_neighbor_set = set(i_feat_neighbor_set.difference(neighbor_set))
    # copy previous set
    new_neighbor_set_copy = set(new_neighbor_set)

    i = 0
    while new_neighbor_set_copy:
        # Loop scan every new neighbor
        for neighbor in new_neighbor_set:
            # set store i_feat neighbor's
            i_feat_neighbor_set = set(adjacency_matrix['matrix'][neighbor])
            # new set of neighbors who have never been scanned before
            new_new_neighbor_set = i_feat_neighbor_set.difference(neighbor_set)
            # add the neighbor to the result list
            neighbor_set.update({neighbor})
            # we add the new neighbors never scanned before
            new_neighbor_set_copy.update(new_new_neighbor_set)

            # we delete the scanned neighbor
            new_neighbor_set_copy = new_neighbor_set_copy.difference({neighbor})

            i += 1
        # adding to new_neighbor_set ew neighbors that have never been scanned before
        new_neighbor_set = set(new_neighbor_set_copy)

    return neighbor_set


def get_neighbor_i_feat(adjacency_matrix, i_feat):
    """
    Return neighbor for given i_feat

    :return:
    """

    return adjacency_matrix["matrix"][i_feat]
