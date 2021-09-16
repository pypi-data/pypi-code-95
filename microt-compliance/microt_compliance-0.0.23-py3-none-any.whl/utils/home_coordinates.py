import pandas as pd
import datetime

import os
from os import listdir
from glob import glob

from sklearn.cluster import DBSCAN, OPTICS

import json
from tqdm import tqdm
import numpy as np

from collections import Counter


# get_home_boarder_coordinates() is the main function:
# Get the max Latitude, min Latitude, max Longitude, min Longitude coordinates of home for each participant.
# e.g., {'XXX': [40.82849023, 40.82956608, -73.62032694, -73.61905812]}

def get_home_boarder_coordinates(participant_ids, microt_root_path):
    participants_home_boarders = {}
    for p_id in tqdm(participant_ids):
        print(p_id)
        df_p = pd.DataFrame()
        participant_path = os.path.join(*[microt_root_path, "intermediate_file",  p_id])
        date_list = listdir(participant_path)

        for date in date_list:
            date_path = os.path.join(participant_path, date)
            csv_path = glob(os.path.join(date_path, 'phone_GPS_clean*.csv'))
            if len(csv_path) > 0:
                df = pd.read_csv(csv_path[0])
                df_p = pd.concat([df_p, df])
        boarder_coords = find_home_individual_box(df_p)
        participants_home_boarders[p_id] = boarder_coords
    return participants_home_boarders


def find_home_individual_box(df_p):
    # Step1: filter out night time (0-5am) location
    df_night_gps_r = subset_night_location(df_p)

    # Step2: find the largest cluster during night as the home cluster
    kms_per_radian = 6371.0088
    epsilon = .02 / kms_per_radian
    home_list = find_home_cluster(df_night_gps_r, epsilon)

    # Step3: find the four extreme coordinates of the bounding box of the home cluster
    df_night_gps = df_p[df_p["night"] == 1][['LAT', 'LONG']]
    boarder_coords = find_boarder_coordinates(df_night_gps, home_list)

    return boarder_coords


def subset_night_location(df_p):
    datetime_list = [datetime.datetime.strptime(x.strip(x.split(' ')[2]).strip(" "), '%Y-%m-%d %H:%M:%S') for x in
                     df_p['LOCATION_TIME']]

    hour_list = []
    for i in range(len(datetime_list)):
        hour_list.append(datetime_list[i].hour)

    night_list = [1 if x < 6 else 0 for x in hour_list]

    df_p["night"] = night_list
    df_p['lat_r'] = np.radians(df_p['LAT'])
    df_p['long_r'] = np.radians(df_p['LONG'])
    df_night_gps_r = df_p[df_p["night"] == 1][['lat_r', 'long_r']]
    df_night_gps_r.reset_index(inplace=True, drop=True)

    return df_night_gps_r


def find_home_cluster(df_night_gps_r, epsilon):
    coords = df_night_gps_r.values

    clusterer_dbscan = OPTICS(eps=epsilon, metric='haversine', cluster_method='dbscan', algorithm='ball_tree')
    clusterer_dbscan.fit(coords)
    cluster_result_list = clusterer_dbscan.labels_

    cluster_value = Counter(cluster_result_list).most_common(1)[0][0]
    home_list = [1 if x == cluster_value else 0 for x in cluster_result_list]

    return home_list


def find_boarder_coordinates(df_night_gps, home_list):
    df_night_gps['Home'] = home_list

    df_home = df_night_gps[df_night_gps['Home'] == 1]

    adjustment = 0.0001 * 3
    long_max = max(df_home['LONG']) + adjustment
    long_min = min(df_home['LONG']) - adjustment
    lat_max = max(df_home['LAT']) + adjustment
    lat_min = min(df_home['LAT']) - adjustment
    return [lat_min, lat_max, long_min, long_max]


if __name__ == "__main__":
    participant_ids = ["bondlesspessimistlivestock", "capitolreferableswinging", "conductorpushpindepth",
                       "dimnesscranialunheard", "eskimovocalizeveggie", "fontsixtyfoldvocally",
                       "gullyskinheadpleat", "hacksawscoldingdares", "reggaeascendactivity",
                       "shrankdicesprain", "shushsaddenenactment", "spideraffixreptilian"]
    microt_root_path = r"E:\intermediate_file"
    result = get_home_boarder_coordinates(participant_ids, microt_root_path)
    with open(r'E:\preliminary_data\OSM\home_boarder_coords.json', 'w') as fp:
        json.dump(result, fp, sort_keys=True, indent=4)
