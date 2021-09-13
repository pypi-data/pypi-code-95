from geoformat.explore_data.print_data import print_features_data_table, print_metadata_field_table
import time


def measure_time(func):
    def time_it(*args, **kwargs):
        time_started = time.time()
        func(*args, **kwargs)
        time_elapsed = time.time()
        print("{execute} running time is {sec} seconds".format(
            execute=func.__name__,
            sec=round(time_elapsed - time_started, 4)
            )
        )

    return time_it


def compare_geolayer(geolayer_a, geolayer_b):

    # compare this two version
    geolayer_a_metadata = print_metadata_field_table(geolayer_a)
    geolayer_b_metadata = print_metadata_field_table(geolayer_b)

    print('FIELDS METADATA')

    metadata_list = [geolayer_a_metadata, geolayer_b_metadata]
    lines = [metadata_list[i].splitlines() for i in range(len(metadata_list))]
    for l in zip(*lines):
        print(*l, sep='\t')



    print('ATTRIBUTES')
    for i_feat in geolayer_a['features']:
        geolayer_a_feature = geolayer_a['features'][i_feat]
        geolayer_b_feature = geolayer_b['features'][i_feat]
        if geolayer_a_feature != geolayer_b_feature:
            if geolayer_a_feature.get('attributes') != geolayer_b_feature.get('attributes'):
                print(i_feat, 'attributes_diff')
                print('\t', geolayer_a_feature.get('attributes'))
                print('\t', geolayer_b_feature.get('attributes'))
            if geolayer_a_feature.get('geometry') != geolayer_b_feature.get('geometry'):
                print(i_feat, 'geometry_diff')
                print('\t', geolayer_a_feature.get('geometry'))
                print('\t', geolayer_b_feature.get('geometry'))