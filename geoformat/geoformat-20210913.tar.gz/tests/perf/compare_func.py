import geoformat
import time
import psycopg2


table_dict = {
    "ocean_0_r17_v18": None,
    # "ocean_1_r16_v17": None,
    # "ocean_2_r15_v16": None,
    # "ocean_3_r14_v15": None,
    # "ocean_5_r13_v14": None,
    # "ocean_10_r12_v13": None,
    # "ocean_20_r11_v12": None,
    # "ocean_40_r10_v11": None,  ## start here
    # "ocean_78_r9_v10": None,
    # "ocean_156_r8_v9": None,
    # "ocean_312_r7_v8": None,
    # "ocean_625_r6_v7": None,
    # "ocean_1250_r5_v6": None,
    # "ocean_2500_r4_v5": None,
    # "ocean_5000_r3_v4": None,
    # "ocean_10000_r2_v3": None,
}



extent = (-5009387.0, 10.0, 4031455.0, 10018744.0)

def get_geolayer_stats(geolayer):

    nb_features = len(geolayer['features'])
    nb_coordinates_list = [None] * nb_features
    area_list = [None] * nb_features
    geolayer_bbox = None
    min_coordinates = None
    min_coordinates_i_feat = None
    max_coordinates = None
    max_coordinates_i_feat = None
    for i, (i_feat, feature) in enumerate(geolayer['features'].items()):
        feature_geometry = feature.get('geometry')
        feature_nb_coordinates = 0.
        feature_area = 0.
        if feature_geometry:
            feature_nb_coordinates = len(list(geoformat.coordinates_to_point(feature_geometry['coordinates'])))
            feature_area = geoformat.geometry_area(feature_geometry)
            feature_bbox = feature_geometry['bbox']
            if geolayer_bbox is None:
                geolayer_bbox = feature_bbox
            else:
                geolayer_bbox = geoformat.bbox_union(geolayer_bbox,  feature_bbox)
            # compute min_coordinates
            if min_coordinates:
                if feature_nb_coordinates < min_coordinates:
                    min_coordinates = feature_nb_coordinates
                    min_coordinates_i_feat = i_feat
            else:
                min_coordinates = feature_nb_coordinates
                min_coordinates_i_feat = i_feat

            # compute max_coordinates
            if max_coordinates:
                if feature_nb_coordinates > max_coordinates:
                    max_coordinates = feature_nb_coordinates
                    max_coordinates_i_feat = i_feat
            else:
                max_coordinates = feature_nb_coordinates
                max_coordinates_i_feat = i_feat


        nb_coordinates_list[i] = feature_nb_coordinates
        area_list[i] = feature_area

    # coordinates stats
    sum_nb_coordinates = sum(nb_coordinates_list)
    mean_nb_coordinates = sum_nb_coordinates / nb_features
    # area stats
    sum_area = sum(area_list)
    mean_area = sum_area / nb_features
    return {
        'geolayer_bbox': geolayer_bbox,
        'nb_features': float(nb_features),
        'nb_coordinates': float(sum_nb_coordinates),
        'min_coordinates': float(min_coordinates),
        'min_coordinates_i_feat': float(min_coordinates_i_feat),
        'mean_coordinates': float(mean_nb_coordinates),
        'max_coordinates': float(max_coordinates),
        'max_coordinates_i_feat': float(max_coordinates_i_feat),
        'sum_area': float(sum_area),
        'mean_area': float(mean_area),
    }


def launch_geoformat_simplify(geolayer, tolerance, algo='RDP'):

    geoalyer_nb_features =  len(geolayer['features'])
    simplify_time_list = [0] * len(geolayer['features'])
    simplify_time_max = None
    time_max_i_feat = None
    simplify_time_min = None
    time_min_i_feat = None
    for i, (i_feat, feature) in enumerate(geolayer['features'].items()):
        feature_geometry = feature.get('geometry')
        if feature_geometry:
            simplify_start = time.time()
            geoformat.simplify(geometry=feature_geometry, tolerance=tolerance, algo=algo)
            simplify_time = (time.time() - simplify_start) * 1000
            simplify_time_list[i] = simplify_time
            # compute time_max
            if simplify_time_max:
                if simplify_time > simplify_time_max:
                    simplify_time_max = simplify_time
                    time_max_i_feat = i_feat
            else:
                simplify_time_max = simplify_time
                time_max_i_feat = i_feat
            # compute time_min
            if simplify_time_min:
                if simplify_time < simplify_time_min:
                    simplify_time_min = simplify_time
                    time_min_i_feat = i_feat
            else:
                simplify_time_min = simplify_time
                time_min_i_feat = i_feat


    simplify_time_sum = sum(simplify_time_list)
    simplify_time_mean = simplify_time_sum/ geoalyer_nb_features
    simplify_time_list.sort()
    simplify_median = simplify_time_list[int(geoalyer_nb_features/2)]

    return {
        '{algo}_time_sum'.format(algo=algo): float(simplify_time_sum),
        '{algo}_time_min'.format(algo=algo): float(simplify_time_min),
        '{algo}_time_min_i_feat'.format(algo=algo): float(time_min_i_feat),
        '{algo}_time_mean'.format(algo=algo): float(simplify_time_mean),
        '{algo}_time_median'.format(algo=algo): float(simplify_median),
        '{algo}_time_max'.format(algo=algo): float(simplify_time_max),
        '{algo}_time_max_i_feat'.format(algo=algo): float(time_max_i_feat)
    }

def launch_postgresql_simplify(geolayer, cursor, tolerance, algo='st_simplify'):

    geoalyer_nb_features =  len(geolayer['features'])
    simplify_time_list = [0] * len(geolayer['features'])
    simplify_time_max = None
    time_max_i_feat = None
    simplify_time_min = None
    time_min_i_feat = None
    for i, (i_feat, feature) in enumerate(geolayer['features'].items()):
        feature_geometry = feature.get('geometry')
        if feature_geometry:
            geometry_wkb = geoformat.geometry_to_wkb(feature_geometry)
            simplify_start = time.time()
            request = "SELECT {algo}(%(geom)s::geometry, {tolerance});".format(
                algo=algo,
                tolerance=tolerance,
            )
            cursor.execute(
                request,
                {'geom': geometry_wkb.hex()}
            )
            simplify_time = (time.time() - simplify_start) * 1000
            simplify_time_list[i] = simplify_time
            # compute time_max
            if simplify_time_max:
                if simplify_time > simplify_time_max:
                    simplify_time_max = simplify_time
                    time_max_i_feat = i_feat
            else:
                simplify_time_max = simplify_time
                time_max_i_feat = i_feat
            # compute time_min
            if simplify_time_min:
                if simplify_time < simplify_time_min:
                    simplify_time_min = simplify_time
                    time_min_i_feat = i_feat
            else:
                simplify_time_min = simplify_time
                time_min_i_feat = i_feat


    simplify_time_sum = sum(simplify_time_list)
    simplify_time_mean = simplify_time_sum/ geoalyer_nb_features
    simplify_time_list.sort()
    simplify_median = simplify_time_list[int(geoalyer_nb_features/2)]

    return {
        '{algo}_time_sum'.format(algo=algo): float(simplify_time_sum),
        '{algo}_time_min'.format(algo=algo): float(simplify_time_min),
        '{algo}_time_min_i_feat'.format(algo=algo): float(time_min_i_feat),
        '{algo}_time_mean'.format(algo=algo): float(simplify_time_mean),
        '{algo}_time_median'.format(algo=algo): float(simplify_median),
        '{algo}_time_max'.format(algo=algo): float(simplify_time_max),
        '{algo}_time_max_i_feat'.format(algo=algo): float(time_max_i_feat)
    }


if __name__ == '__main__':
    host = "localhost"
    user = 'redpig'
    pwd = 'Flostib4'
    port = 5433
    bd_name = 'world_ic_night_2006'
    schema = 'map'

    # connect to database
    conn_string = "host={host} user={user} dbname={dbname} password={password} port={port}".format(
        host=host,
        user=user,
        password=pwd,
        dbname=bd_name,
        port=port)

    pg_adress = 'PG: {conn_string} schemas={schemas}'.format(conn_string=conn_string, schemas=schema)
    print(conn_string)
    print(pg_adress)
    database_connection = psycopg2.connect(conn_string)
    cursor = database_connection.cursor()

    begin_loop_time = time.time()
    output_features_list = []
    for table_name, value in table_dict.items():
        open_geolayer_time = time.time()
        geolayer = geoformat.ogr_layer_to_geolayer(
            path=pg_adress,
            layer_id_or_name=table_name,
            bbox_extent=True,
            bbox_filter=extent,
        )
        print(table_name)
        tolerance_rdp = int(table_name.split('_')[1])
        tolerance_vw = tolerance_rdp ** 2
        print('\t get geolayer time', time.time() - open_geolayer_time)
        output_feature = {'attributes': {}}
        for key, value in get_geolayer_stats(geolayer).items():
            print('\t', key, value)
            output_feature['attributes'][key] = value
        for key, value in launch_geoformat_simplify(geolayer, tolerance=tolerance_rdp, algo='RDP').items():
            print('\t', key, value)
            output_feature['attributes'][key] = value
        for key, value in launch_geoformat_simplify(geolayer, tolerance=tolerance_vw, algo='VW').items():
            print('\t', key, value)
            output_feature['attributes'][key] = value
        for key, value in launch_postgresql_simplify(geolayer, cursor=cursor, tolerance=tolerance_rdp, algo='st_simplify').items():
            print('\t', key, value)
            output_feature['attributes'][key] = value
        for key, value in launch_postgresql_simplify(geolayer, cursor=cursor, tolerance=tolerance_rdp, algo='st_simplifyVW').items():
            print('\t', key, value)
            output_feature['attributes'][key] = value

        output_features_list.append(output_feature)
    print('loop time', time.time() - begin_loop_time)
output_geolayer = geoformat.feature_list_to_geolayer(feature_list=output_features_list, geolayer_name='simplify_stat')

geoformat.geolayer_to_ogr_layer(geolayer=output_geolayer, path='simplify_stat.csv', driver_name='CSV')