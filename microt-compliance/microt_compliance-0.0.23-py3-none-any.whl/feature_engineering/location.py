from os import path, sep, makedirs
from glob import glob
import pandas as pd
import numpy as np
import bisect
import requests
from tqdm import tqdm
import pickle

from microt_compliance_matrix.utils.validate_date import *


def combine_intermediate_file(participants_ids, intermediate_root_path, feature_save_path, start_date, end_date):
    df_combined = pd.DataFrame()
    for p_id in participants_ids:
        participant_logs_path = intermediate_root_path + sep + "intermediate_file" + sep + p_id

        # step 1: generate date range where date folder exists (sharable code in utils)
        validated_date_list = validate_date(participant_logs_path, start_date, end_date)
        if len(validated_date_list) == 0:
            print("Cannot find date folder in data source between {} and {}".format(start_date, end_date))
            return None

        for date in validated_date_list:
            date_folder_path = participant_logs_path + sep + date
            csv_path_list = sorted(glob(os.path.join(date_folder_path, 'phone_GPS_clean*.csv')))  # file name
            if len(csv_path_list) == 0:
                print("No GPS daily file on {}".format(date))
                continue

            csv_path = csv_path_list[0]
            df_daily = pd.read_csv(csv_path)
            if df_daily.shape[0] > 0:
                df_daily['Participant_ID'] = [p_id] * df_daily.shape[0]
                df_combined = pd.concat([df_combined, df_daily])

    # save a copy of combined file in compliance anaysis folder
    save_path = feature_save_path + sep + "compliance_analysis" + sep + "uEMA_plus" + sep + "location"
    if df_combined.shape[0] > 0:
        if not path.exists(save_path):
            makedirs(save_path)
        df_combined.reset_index(inplace=True, drop=True)
        df_combined.to_csv(save_path + sep + "combined.csv", index=False)

    return df_combined


def find_closest_time(prompt_time, subset_time_list):
    i = bisect.bisect_left(subset_time_list, prompt_time)
    closet_time = min(subset_time_list[max(0, i - 1): i + 2], key=lambda t: abs(prompt_time - t))
    return closet_time


def match_feature(feature_save_path, prompt_feature_df, df_gps_combined):
    print("     --- start transformation\n")
    converter = lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f")
    prompt_feature_df['PROMPT_TIMESTAMP'] = pd.Series(map(converter, prompt_feature_df['PROMPT_LOCAL_TIME']))
    df_gps_combined["LOCATION_TIME"] = [x.strip(x.split(' ')[2]).strip(" ") for x in
                                        list(df_gps_combined["LOCATION_TIME"])]
    converter2 = lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
    df_gps_combined['LOCATION_TIMESTAMP'] = pd.Series(map(converter2, df_gps_combined["LOCATION_TIME"]))
    df_gps_combined['Date'] = df_gps_combined['LOCATION_TIMESTAMP'].dt.date

    print("     --- start matching\n")
    matched_info_list = []
    for idx in tqdm(prompt_feature_df.index):
        p_id = prompt_feature_df['Participant_ID'][idx]
        prompt_time = prompt_feature_df['PROMPT_TIMESTAMP'][idx]
        prompt_date = prompt_time.date()

        df_gps_participant = df_gps_combined[df_gps_combined['Participant_ID'] == p_id][
            df_gps_combined['Date'] == prompt_date]
        if df_gps_participant.shape[0] == 0:
            location = np.nan
        else:
            # print(df_gps_participant["START_TIMESTAMP"][df_gps_participant.shape[0]-20])
            subset_time_list = list(df_gps_participant["LOCATION_TIMESTAMP"])

            closest_time = find_closest_time(prompt_time, subset_time_list)
            target_idx = df_gps_participant['LOCATION_TIMESTAMP'] == closest_time
            lat = list(df_gps_participant[target_idx]['LAT'])[0]
            long = list(df_gps_participant[target_idx]['LONG'])[0]
            location = [lat, long]

        matched_info_list.append(location)

        if idx % 1000 == 0:
            matched_save_path = os.path.join(*[feature_save_path, "compliance_analysis", "location", "matched_location_list.txt"])

            with open(matched_save_path, "wb") as fp:
                pickle.dump(matched_info_list, fp)

    return matched_info_list


def reverse_geo_nominatim(lat, long):
    URL = "https://nominatim.openstreetmap.org/reverse?"
    PARAMS = {'format': 'geojson', 'lat': lat, 'lon': long}
    r = requests.get(url=URL, params=PARAMS)
    result = r.json()

    category = result['features'][0]['properties']['category']
    type_loc = result['features'][0]['properties']['type']

    location = [category, type_loc]
    return location


#     # here introduces the OpenStreetMap API
# def transform(location_column):
#     result_list = []
#     for gps_pair in location_column:
#         result = reverse_geo_nominatim(gps_pair[0], gps_pair[1])
#         result_list.append(result)
#         print(result)
#     return result_list
def transform(location_column):
    return location_column


def create_column(prompt_feature_df, intermediate_root_path, feature_save_path, start_date, end_date):
    print("\n> start generating the feature: location ")
    participants_ids = prompt_feature_df['Participant_ID'].unique()

    # Read, parse and combine related intermediate file
    df_combined = combine_intermediate_file(participants_ids, intermediate_root_path, feature_save_path, start_date,
                                            end_date)
    # df_combined = pd.read_csv(r"E:\compliance_analysis\location\combined.csv")
    # Match the combined parsed intermediate file with prompt feature data frame
    location_column = match_feature(feature_save_path, prompt_feature_df, df_combined)

    # transform feature
    location_column_transformed = transform(location_column)

    return location_column_transformed


if __name__ == "__main__":
    gps_list = [[42.340702, -71.117756]]
    print(transform(gps_list))
