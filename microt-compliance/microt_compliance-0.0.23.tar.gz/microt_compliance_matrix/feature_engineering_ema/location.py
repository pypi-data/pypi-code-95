import os
from os import sep
from glob import glob
import pandas as pd
import numpy as np
import bisect
# from tqdm import tqdm
from datetime import datetime, timedelta
from microt_compliance_matrix import utils

from microt_compliance_matrix.utils.uncompress_file import *

target_file_pattern = 'phone_GPS_clean*.csv.zip'

def validate_dates_before_after(intermediate_participant_path, date_in_study):
    validated_date_list = []

    # target date
    date_folder_path = intermediate_participant_path + sep + date_in_study
    target_date_log_paths = sorted(glob(os.path.join(date_folder_path, target_file_pattern)))  # file name
    if len(target_date_log_paths) == 0:
        print("No battery daily file on {}".format(date_in_study))
    else:

        # 1 day before target date
        date_format = "%Y-%m-%d"
        one_date_before_datetime = datetime.strptime(date_in_study, date_format).date() - timedelta(days=1)
        one_date_before = one_date_before_datetime.strftime(date_format)
        date_folder_path = intermediate_participant_path + sep + one_date_before
        one_day_before_log_paths = sorted(glob(os.path.join(date_folder_path, target_file_pattern)))  # file name
        if len(one_day_before_log_paths) != 0:
            validated_date_list.append(one_date_before)

        # target date
        validated_date_list.append(date_in_study)

        # 1 day after target date
        date_format = "%Y-%m-%d"
        one_date_after_datetime = datetime.strptime(date_in_study, date_format).date() + timedelta(days=1)
        one_date_after = one_date_after_datetime.strftime(date_format)
        date_folder_path = intermediate_participant_path + sep + one_date_after
        one_day_after_log_paths = sorted(glob(os.path.join(date_folder_path, target_file_pattern)))  # file name
        if len(one_day_after_log_paths) != 0:
            validated_date_list.append(one_date_after)


    return validated_date_list

def combine_intermediate_file(intermediate_participant_path, date_in_study, decryption_password):
    df_logs_combined = pd.DataFrame()
    participant_id = utils.extract_participant_id.extract_participant_id(intermediate_participant_path)

    # generate date range where date folder exists (sharable code in utils)
    validated_date_list = validate_dates_before_after(intermediate_participant_path, date_in_study)
    if len(validated_date_list) == 0:
        print("Cannot find logs file around {}".format(date_in_study))
        return df_logs_combined

    for date in validated_date_list:
        date_folder_path = intermediate_participant_path + sep + date
        csv_path_list = sorted(glob(os.path.join(date_folder_path, target_file_pattern)))  # file name

        csv_path = csv_path_list[0]

        # decryption
        unzip_file_path = uncompress(csv_path, decryption_password)

        try:
            df_day = pd.read_csv(unzip_file_path)
        except pd.errors.EmptyDataError:
            print("pandas.errors.EmptyDataError (location) : " + unzip_file_path)
            quit()

        if df_day.shape[0] > 0:
            df_day['Participant_ID'] = [participant_id] * df_day.shape[0]
            df_logs_combined = pd.concat([df_logs_combined, df_day])
        delete_unzipped_file(unzip_file_path)

    converter = lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
    df_logs_combined = df_logs_combined.dropna(subset=['LOCATION_TIME'])
    df_logs_combined.reset_index(inplace=True, drop=True)
    df_logs_combined["LOCATION_TIME"] = [x.split(" ")[0] + " " + x.split(" ")[1] for x in
                                         list(df_logs_combined["LOCATION_TIME"])]

    df_logs_combined['LOCATION_TIME_DATETIME'] = pd.Series(map(converter, df_logs_combined["LOCATION_TIME"]))
    df_logs_combined['Date'] = df_logs_combined['LOCATION_TIME_DATETIME'].dt.date

    return df_logs_combined


def find_closest_time(prompt_time, subset_time_list):
    i = bisect.bisect_left(subset_time_list, prompt_time)
    closet_time = min(subset_time_list[max(0, i - 1): i + 2], key=lambda t: abs(prompt_time - t))
    return closet_time


def match_feature(prompt_local_datetime_series, df_logs_combined):

    print("     --- start matching")
    matched_location_list = []

    for idx in prompt_local_datetime_series.index:
        prompt_time = prompt_local_datetime_series[idx]
        # prompt_date = prompt_time.date()


        if df_logs_combined.shape[0] == 0:
            location = np.nan
        else:
            subset_time_list = list(df_logs_combined["LOCATION_TIME_DATETIME"])

            closest_time = find_closest_time(prompt_time, subset_time_list)

            lat = list(df_logs_combined[df_logs_combined['LOCATION_TIME_DATETIME'] == closest_time][
                                     "LAT"])[0]
            long = list(df_logs_combined[df_logs_combined['LOCATION_TIME_DATETIME'] == closest_time][
                                       "LONG"])[0]
            location = [lat, long]

        matched_location_list.append(location)


    return matched_location_list


# def reverse_geo_nominatim(lat, long):
#     URL = "https://nominatim.openstreetmap.org/reverse?"
#     PARAMS = {'format': 'geojson', 'lat': lat, 'lon': long}
#     r = requests.get(url=URL, params=PARAMS)
#     result = r.json()
#
#     category = result['features'][0]['properties']['category']
#     type_loc = result['features'][0]['properties']['type']
#
#     location = [category, type_loc]
#     return location


def transform(location_column):
    return location_column


def create_column(prompt_local_datetime_series, intermediate_participant_path, date_in_study, decryption_password):
    print("\n> start generating the feature: Location ")

    # Read, parse and combine related intermediate file
    df_logs_combined = combine_intermediate_file(intermediate_participant_path, date_in_study, decryption_password)

    if df_logs_combined.shape[0] > 0:
        # Match the combined parsed intermediate file with prompt feature data frame
        location_column = match_feature(prompt_local_datetime_series, df_logs_combined)
    else:
        location_column = ["NF"] * len(prompt_local_datetime_series)

    # transform feature
    location_column_transformed = transform(location_column)
    print("     --- success")

    return location_column_transformed


if __name__ == "__main__":
    gps_list = [[42.340702, -71.117756]]
    print(transform(gps_list))
