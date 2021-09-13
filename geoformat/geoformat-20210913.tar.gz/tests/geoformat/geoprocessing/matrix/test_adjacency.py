from geoformat.geoprocessing.matrix.adjacency import (
    create_adjacency_matrix,
    get_neighbor_i_feat,
    get_area_intersecting_neighbors_i_feat
)

from test_all import (
    test_function,
    test_dependencies
)

from tests.data.geolayers import geolayer_grid_3_3
from tests.data.matrix import matrix_grid_3_3

create_adjacency_matrix_parameters = {
    0:  {
        'geolayer': geolayer_grid_3_3,
        'mesh_size': None,
        'return_value': matrix_grid_3_3
    }
}

get_neighbor_i_feat_parameters = {
    0: {
        "adjacency_matrix": matrix_grid_3_3,
        "i_feat": 4,
        "return_value": {0, 1, 2, 3, 5, 6, 7, 8}
    },
    1: {
        "adjacency_matrix": matrix_grid_3_3,
        "i_feat": 8,
        "return_value": {4, 5, 7,}
    },
}

get_area_intersecting_neighbors_i_feat_parameters = {
    0: {
        'adjacency_matrix': matrix_grid_3_3,
        'i_feat': 4,
        'neighbor_set': None,
        "return_value": {0, 1, 2, 3, 4, 5, 6, 7, 8}
    },
    1: {
        'adjacency_matrix': matrix_grid_3_3,
        'i_feat': 0,
        'neighbor_set': None,
        "return_value": {0, 1, 2, 3, 4, 5, 6, 7, 8}
    }
}


def test_all():

    if test_dependencies()['ogr']:
        # create_adjacency_matrix
        print(test_function(create_adjacency_matrix, create_adjacency_matrix_parameters))

    # get_neighbor_i_feat
    print(test_function(get_neighbor_i_feat, get_neighbor_i_feat_parameters))

    # get_area_intersecting_neighbors_i_feat
    print(test_function(get_area_intersecting_neighbors_i_feat, get_area_intersecting_neighbors_i_feat_parameters))


if __name__ == '__main__':
    test_all()
