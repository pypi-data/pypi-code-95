from geoformat.conversion.coordinates_conversion import (
    format_coordinates,
    coordinates_to_2d_coordinates,
    coordinates_to_centroid
)

from tests.data.coordinates import (
    coordinates_with_list,
    coordinates_with_tuple,
    coordinates_with_duplicated_coordinates,
    point_coordinates,
    linestring_coordinates,
    polygon_coordinates,
    multipoint_coordinates,
    multilinestring_coordinates,
    multipolygon_coordinates,
    point_coordinates_3d,
    linestring_coordinates_3d,
    polygon_coordinates_3d,
    multipoint_coordinates_3d,
    multilinestring_coordinates_3d,
    multipolygon_coordinates_3d,
)
from test_all import test_function

try:
    import pyproj

    import_pyproj_success = True
except ImportError:
    import_pyproj_success = False


format_coordinates_parameters = {
    0: {
        "coordinates_list_tuple": coordinates_with_list,
        "format_to_type": list,
        "precision": None,
        "delete_duplicate_following_coordinates": False,
        "return_value": [[[650942.200000008, 6857645.800000944], [645325.1000000088, 6859675.200000941], [643644.0000000091, 6863500.900000929]], [[670055.5000000049, 6856451.100000947], [671600.3000000048, 6851282.800000963]]]
    },
    1: {
        "coordinates_list_tuple": coordinates_with_tuple,
        "format_to_type": list,
        "precision": None,
        "delete_duplicate_following_coordinates": False,
        "return_value": [[[650942.200000008, 6857645.800000944], [645325.1000000088, 6859675.200000941], [643644.0000000091, 6863500.900000929]], [[670055.5000000049, 6856451.100000947], [671600.3000000048, 6851282.800000963]]]
    },
    2: {
        "coordinates_list_tuple": coordinates_with_list,
        "format_to_type": tuple,
        "precision": None,
        "delete_duplicate_following_coordinates": False,
        "return_value": (((650942.200000008, 6857645.800000944), (645325.1000000088, 6859675.200000941), (643644.0000000091, 6863500.900000929)), ((670055.5000000049, 6856451.100000947), (671600.3000000048, 6851282.800000963)))

    },
    3: {
        "coordinates_list_tuple": coordinates_with_tuple,
        "format_to_type": tuple,
        "precision": None,
        "delete_duplicate_following_coordinates": False,
        "return_value": (((650942.200000008, 6857645.800000944), (645325.1000000088, 6859675.200000941), (643644.0000000091, 6863500.900000929)), ((670055.5000000049, 6856451.100000947), (671600.3000000048, 6851282.800000963)))

    },
    4: {
        "coordinates_list_tuple": coordinates_with_list,
        "format_to_type": list,
        "precision": 0,
        "delete_duplicate_following_coordinates": False,
        "return_value": [[[650942., 6857646.], [645325., 6859675.], [643644., 6863501.]], [[670056., 6856451.], [671600., 6851283.]]]
    },
    5: {
        "coordinates_list_tuple": coordinates_with_tuple,
        "format_to_type": list,
        "precision": 0,
        "delete_duplicate_following_coordinates": False,
        "return_value": [[[650942., 6857646.], [645325., 6859675.], [643644., 6863501.]], [[670056., 6856451.], [671600., 6851283.]]]
    },
    6: {
        "coordinates_list_tuple": coordinates_with_list,
        "format_to_type": tuple,
        "precision": 0,
        "delete_duplicate_following_coordinates": False,
        "return_value": (((650942., 6857646.), (645325., 6859675.), (643644., 6863501.)), ((670056., 6856451.), (671600., 6851283.)))
    },
    7: {
        "coordinates_list_tuple": coordinates_with_tuple,
        "format_to_type": tuple,
        "precision": 0,
        "delete_duplicate_following_coordinates": False,
        "return_value": (((650942., 6857646.), (645325., 6859675.), (643644., 6863501.)), ((670056., 6856451.), (671600., 6851283.)))
    },
    8: {
        "coordinates_list_tuple": coordinates_with_list,
        "format_to_type": list,
        "precision": 1,
        "delete_duplicate_following_coordinates": False,
        "return_value": [[[650942.2, 6857645.8], [645325.1, 6859675.2], [643644.0, 6863500.9]], [[670055.5, 6856451.1], [671600.3, 6851282.8]]]
    },
    9: {
        "coordinates_list_tuple": coordinates_with_tuple,
        "format_to_type": list,
        "precision": 1,
        "delete_duplicate_following_coordinates": False,
        "return_value": [[[650942.2, 6857645.8], [645325.1, 6859675.2], [643644.0, 6863500.9]], [[670055.5, 6856451.1], [671600.3, 6851282.8]]]
    },
    10: {
        "coordinates_list_tuple": coordinates_with_duplicated_coordinates,
        "format_to_type": list,
        "precision": None,
        "delete_duplicate_following_coordinates": True,
        "return_value": [[[650942.200000008, 6857645.800000944], [645325.1000000088, 6859675.200000941], [643644.0000000091, 6863500.900000929]], [[670055.5000000049, 6856451.100000947], [671600.3000000048, 6851282.800000963]], [[799606.7999999593, 6263118.800002612], [825917.6999999485, 6262029.800002615]], [[869889.3999999303, 6258065.200002626], [866898.8999999315, 6258271.7000026265], [866104.2999999323, 6264876.400002609], [862373.7999999337, 6265459.30000261]]]
    },
    11: {
        "coordinates_list_tuple": coordinates_with_duplicated_coordinates,
        "format_to_type": list,
        "precision": None,
        "delete_duplicate_following_coordinates": True,
        "return_value": [[[650942.200000008, 6857645.800000944], [645325.1000000088, 6859675.200000941], [643644.0000000091, 6863500.900000929]], [[670055.5000000049, 6856451.100000947], [671600.3000000048, 6851282.800000963]], [[799606.7999999593, 6263118.800002612], [825917.6999999485, 6262029.800002615]], [[869889.3999999303, 6258065.200002626], [866898.8999999315, 6258271.7000026265], [866104.2999999323, 6264876.400002609], [862373.7999999337, 6265459.30000261]]]
    },
    12: {
        "coordinates_list_tuple": coordinates_with_duplicated_coordinates,
        "format_to_type": tuple,
        "precision": None,
        "delete_duplicate_following_coordinates": True,
        "return_value": (((650942.200000008, 6857645.800000944), (645325.1000000088, 6859675.200000941), (643644.0000000091, 6863500.900000929)), ((670055.5000000049, 6856451.100000947), (671600.3000000048, 6851282.800000963)), ((799606.7999999593, 6263118.800002612), (825917.6999999485, 6262029.800002615)), ((869889.3999999303, 6258065.200002626), (866898.8999999315, 6258271.7000026265), (866104.2999999323, 6264876.400002609), (862373.7999999337, 6265459.30000261)))
    },
    13: {
        "coordinates_list_tuple": coordinates_with_duplicated_coordinates,
        "format_to_type": list,
        "precision": 2,
        "delete_duplicate_following_coordinates": True,
        "return_value": [[[650942.2, 6857645.8], [645325.1, 6859675.2], [643644., 6863500.9]], [[670055.5, 6856451.1], [671600.3, 6851282.8]], [[799606.8, 6263118.8], [825917.7, 6262029.8]], [[869889.4, 6258065.2], [866898.9, 6258271.7], [866104.3, 6264876.4], [862373.8, 6265459.3]]]
    },
    14: {
        "coordinates_list_tuple": [[[[650942.200000008, 6857645.800000944], [645325.1000000088, 6859675.200000941],
                                     [645325.1000000088, 6859675.200000941], [643644.0000000091, 6863500.900000929]],
                                    [[670055.5000000049, 6856451.100000947], [671600.3000000048, 6851282.800000963],
                                     [671600.3000000048, 6851282.800000963]],
                                    [[799606.7999999593, 6263118.800002612], [799606.7999999593, 6263118.800002612],
                                     [825917.6999999485, 6262029.800002615]],
                                    [[869889.3999999303, 6258065.200002626], [869889.3999999303, 6258065.200002626],
                                     [866898.8999999315, 6258271.7000026265], [866898.8999999315, 6258271.7000026265],
                                     [866898.8999999315, 6258271.7000026265], [866104.2999999323, 6264876.400002609],
                                     [862373.7999999337, 6265459.30000261], [862373.7999999337, 6265459.30000261],
                                     [862373.7999999337, 6265459.30000261], [862373.7999999337, 6265459.30000261]]], [
                                       [[650952.200000008, 6857635.800000944], [645335.1000000088, 6859665.200000941],
                                        [645335.1000000088, 6859665.200000941], [643654.0000000091, 6863490.900000929]],
                                       [[670065.5000000049, 6856441.100000947], [671610.3000000048, 6851272.800000963],
                                        [671610.3000000048, 6851272.800000963]],
                                       [[799616.7999999593, 6263108.800002612], [799616.7999999593, 6263108.800002612],
                                        [825927.6999999485, 6262019.800002615]],
                                       [[869899.3999999303, 6258055.200002626], [869899.3999999303, 6258055.200002626],
                                        [866908.8999999315, 6258261.7000026265],
                                        [866908.8999999315, 6258261.7000026265],
                                        [866908.8999999315, 6258261.7000026265], [866114.2999999323, 6264866.400002609],
                                        [862383.7999999337, 6265449.30000261], [862383.7999999337, 6265449.30000261],
                                        [862383.7999999337, 6265449.30000261], [862383.7999999337, 6265449.30000261]]]],
        "format_to_type": list,
        "precision": None,
        "delete_duplicate_following_coordinates": True,
        "return_value": [[[[650942.200000008, 6857645.800000944], [645325.1000000088, 6859675.200000941],
                           [643644.0000000091, 6863500.900000929]],
                          [[670055.5000000049, 6856451.100000947], [671600.3000000048, 6851282.800000963]],
                          [[799606.7999999593, 6263118.800002612], [825917.6999999485, 6262029.800002615]],
                          [[869889.3999999303, 6258065.200002626], [866898.8999999315, 6258271.7000026265],
                           [866104.2999999323, 6264876.400002609], [862373.7999999337, 6265459.30000261]]], [
                             [[650952.200000008, 6857635.800000944], [645335.1000000088, 6859665.200000941],
                              [643654.0000000091, 6863490.900000929]],
                             [[670065.5000000049, 6856441.100000947], [671610.3000000048, 6851272.800000963]],
                             [[799616.7999999593, 6263108.800002612], [825927.6999999485, 6262019.800002615]],
                             [[869899.3999999303, 6258055.200002626], [866908.8999999315, 6258261.7000026265],
                              [866114.2999999323, 6264866.400002609], [862383.7999999337, 6265449.30000261]]]]
    },
    15: {
        "coordinates_list_tuple": [[438589.8, 6789320.8], [438565.2, 6789230.3], [438550.0, 6789190.5], [438519.7, 6789145.7], [438479.5, 6789106.1], [438477.2, 6789075.9], [438477.2, 6789075.9]],
        "format_to_type": list,
        "precision": None,
        "delete_duplicate_following_coordinates": True,
        "return_value": [[438589.8, 6789320.8], [438565.2, 6789230.3], [438550.0, 6789190.5], [438519.7, 6789145.7], [438479.5, 6789106.1], [438477.2, 6789075.9]]
    },
    16: {
        "coordinates_list_tuple": [
        [
            [650942.200000008, 6857645.800000944],
            [645325.1000000088, 6859675.200000941],
            [645325.1000000088, 6859675.200000941],
            [643644.0000000091, 6863500.900000929],
        ],
        [
            [670055.5000000049, 6856451.100000947],
            [671600.3000000048, 6851282.800000963],
            [671600.3000000048, 6851282.800000963],
        ],
        [
            [799606.7999999593, 6263118.800002612],
            [799606.7999999593, 6263118.800002612],
            [825917.6999999485, 6262029.800002615],
        ],
        [
            [869889.3999999303, 6258065.200002626],
            [869889.3999999303, 6258065.200002626],
            [866898.8999999315, 6258271.7000026265],
            [866898.8999999315, 6258271.7000026265],
            [866898.8999999315, 6258271.7000026265],
            [866104.2999999323, 6264876.400002609],
            [862373.7999999337, 6265459.30000261],
            [862373.7999999337, 6265459.30000261],
            [862373.7999999337, 6265459.30000261],
            [862373.7999999337, 6265459.30000261],
        ]],
        "format_to_type": list,
        "precision": None,
        "delete_duplicate_following_coordinates": True,
        "return_value": [
        [
            [650942.200000008, 6857645.800000944],
            [645325.1000000088, 6859675.200000941],
            [643644.0000000091, 6863500.900000929],
        ],
        [
            [670055.5000000049, 6856451.100000947],
            [671600.3000000048, 6851282.800000963],
        ],
        [
            [799606.7999999593, 6263118.800002612],
            [825917.6999999485, 6262029.800002615],
        ],
        [
            [869889.3999999303, 6258065.200002626],
            [866898.8999999315, 6258271.7000026265],
            [866104.2999999323, 6264876.400002609],
            [862373.7999999337, 6265459.30000261],
        ]]
    },
    17: {
        "coordinates_list_tuple":  [2.348860390484333, 48.85332408262766],
        "format_to_type": list,
        "precision": None,
        "delete_duplicate_following_coordinates": False,
        "in_crs": 4326,
        "out_crs": 3857,
        "return_value": [261473.94261320567, 6250010.107098978]
    },
    18: {
        "coordinates_list_tuple": coordinates_with_list,
        "format_to_type": list,
        "precision": None,
        "delete_duplicate_following_coordinates": False,
        "in_crs": 2154,
        "out_crs": 4326,
        "return_value": [[[2.3318980606376245, 48.81701092964179], [2.2551442384175053, 48.83480954936943], [2.2317363597468605, 48.86906858161015]], [[2.5922736733656313, 48.80743755195247], [2.613651742567929, 48.761025406730454]]]
    },
    19: {
        "coordinates_list_tuple": coordinates_with_list,
        "format_to_type": list,
        "precision": 2,
        "delete_duplicate_following_coordinates": False,
        "in_crs": 2154,
        "out_crs": 4326,
        "return_value": [[[2.33, 48.82], [2.26, 48.83], [2.23, 48.87]], [[2.59, 48.81], [2.61, 48.76]]]
    },
    20: {
        "coordinates_list_tuple": point_coordinates,
        "format_to_type": list,
        "precision": 5,
        "delete_duplicate_following_coordinates": False,
        "in_crs": 4326,
        "out_crs": 3857,
        "return_value": [-12891910.22877, 4472612.69847]

    },
    21: {
        "coordinates_list_tuple": linestring_coordinates,
        "format_to_type": list,
        "precision": 2,
        "delete_duplicate_following_coordinates": False,
        "in_crs": 4326,
        "out_crs": 3857,
        "return_value": [[992858.54, 5528706.26], [993303.82, 5528721.84]]

    },
    22: {
        "coordinates_list_tuple": multipolygon_coordinates,
        "format_to_type": list,
        "precision": 4,
        "delete_duplicate_following_coordinates": False,
        "in_crs": 4326,
        "out_crs": 3857,
        "return_value": [[[[420787.6752, 1037591.3966], [-14572834.5397, 169225.477], [3909540.5167, 11838014.6714], [420787.6752, 1037591.3966]]], [[[2580385.7966, -4067808.7298], [-145828.5329, -513737.4541], [379599.4636, 14320673.8981], [2580385.7966, -4067808.7298]]]]

    },
}

coordinates_to_2d_coordinates_parameters = {
    0: {
        "coordinates_list": [],
        "return_value": []
    },
    1: {
        "coordinates_list": point_coordinates_3d,
        "return_value": point_coordinates
    },
    2: {
        "coordinates_list": linestring_coordinates_3d,
        "return_value": linestring_coordinates
    },
    3: {
        "coordinates_list": polygon_coordinates_3d,
        "return_value": polygon_coordinates
    },
    4: {
        "coordinates_list": multipoint_coordinates_3d,
        "return_value": multipoint_coordinates
    },
    5: {
        "coordinates_list": multilinestring_coordinates_3d,
        "return_value": multilinestring_coordinates
    },
    6: {
        "coordinates_list": multipolygon_coordinates_3d,
        "return_value": multipolygon_coordinates
    }
}

coordinates_to_centroid_parameters = {
    0: {
        "coordinates_list_tuple": point_coordinates,
        "precision": None,
        "return_value": point_coordinates
    },
    1: {
        "coordinates_list_tuple": linestring_coordinates,
        "precision": None,
        "return_value": [8.921, 44.40745]
    },
    2: {
        "coordinates_list_tuple": polygon_coordinates,
        "precision": None,
        "return_value": [-13.5245,	18.90425]
    },
    3: {
        "coordinates_list_tuple": multipoint_coordinates,
        "precision": 2,
        "return_value": [-156.57, 20.60]
    },
    4: {
        "coordinates_list_tuple": multilinestring_coordinates,
        "precision": 3,
        "return_value": [-20.39, 9.964]
    },
    5: {
        "coordinates_list_tuple": multipolygon_coordinates,
        "precision": 5,
        "return_value": [-4.97125, 12.12925]
    },
}


def test_all():
    if import_pyproj_success is True:
        # format_coordinates
        print(test_function(format_coordinates, format_coordinates_parameters))

    # coordinates_to_2d_coordinates
    print(test_function(coordinates_to_2d_coordinates, coordinates_to_2d_coordinates_parameters))

    # coordinates_to_centroid
    print(test_function(coordinates_to_centroid, coordinates_to_centroid_parameters))


if __name__ == '__main__':
    test_all()