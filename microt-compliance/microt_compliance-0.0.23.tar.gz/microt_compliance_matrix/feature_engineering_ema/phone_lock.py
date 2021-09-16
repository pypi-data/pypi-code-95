import os
from os import sep
from glob import glob
import pandas as pd
import numpy as np
# from tqdm import tqdm
from datetime import datetime, timedelta
from microt_compliance_matrix import utils


target_file_pattern = 'phone_app_usage_clean*.csv'

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

def combine_intermediate_file(intermediate_participant_path, date_in_study):
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

        try:
            df_day = pd.read_csv(csv_path)
        except pd.errors.EmptyDataError:
            raise Exception("pandas.errors.EmptyDataError (phone_lock) : " + csv_path)

        if df_day.shape[0] > 0:
            df_day['Participant_ID'] = [participant_id] * df_day.shape[0]
            df_logs_combined = pd.concat([df_logs_combined, df_day])

    # filter out irrelevant logs
    df_logs_combined = df_logs_combined[df_logs_combined['APP_EVENT'].isin(["KEYGUARD_HIDDEN", "KEYGUARD_SHOWN"])]
    df_logs_combined.reset_index(inplace=True, drop=True)

    converter = lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f")
    df_logs_combined = df_logs_combined.dropna(subset=['EVENT_TIME'])
    df_logs_combined.reset_index(inplace=True, drop=True)
    df_logs_combined["EVENT_TIME"] = [x.split(" ")[0] + " " + x.split(" ")[1] for x in
                                         list(df_logs_combined["EVENT_TIME"])]

    df_logs_combined['EVENT_TIME_DATETIME'] = pd.Series(map(converter, df_logs_combined["EVENT_TIME"]))
    if df_logs_combined.shape[0] > 0:
        df_logs_combined['Date'] = df_logs_combined['EVENT_TIME_DATETIME'].dt.date

    return df_logs_combined


# def find_closest_time(prompt_time, subset_time_list):
#     i = bisect.bisect_left(subset_time_list, prompt_time)
#     closet_time = min(subset_time_list[max(0, i - 1): i + 2], key=lambda t: abs(prompt_time - t))
#     return closet_time
def find_prev_closest_time(prompt_time, subset_time_list):
    previous_timestamps = subset_time_list[subset_time_list < prompt_time]
    reverse = False
    if len(previous_timestamps) > 0:
        closet_time = previous_timestamps.max()
    else:
        after_timestamps = subset_time_list[subset_time_list > prompt_time]
        closet_time = after_timestamps.min()
        reverse = True
    return closet_time, reverse


def calculate_duration(prompt_time, closest_time):
    # print(prompt_time)
    # print(closest_time)
    # print("\\")
    # dur = (prompt_time-closest_time).seconds
    dur = round((prompt_time-closest_time).seconds / 60, 1)
    if dur > 60:
        dur = 60
    return dur


def match_feature(prompt_local_datetime_series, df_logs_combined):
    print("     --- start matching")
    matched_phone_lock_list = []
    matched_last_usage_list = []

    for idx in prompt_local_datetime_series.index:
        prompt_time = prompt_local_datetime_series[idx]
        # prompt_date = prompt_time.date()

        if df_logs_combined.shape[0] == 0:
            location = np.nan
        else:
            subset_time_series = df_logs_combined["EVENT_TIME_DATETIME"]

            closest_time, reverse = find_prev_closest_time(prompt_time, subset_time_series)

            phone_event = list(df_logs_combined[df_logs_combined['EVENT_TIME_DATETIME'] == closest_time][
                                     "APP_EVENT"])[0]


            # to determine phone on/off
            if not reverse:
                if phone_event == "KEYGUARD_HIDDEN":
                    phone_lock = "Phone Unlocked"
                    last_usage = 0
                elif phone_event == "KEYGUARD_SHOWN":
                    phone_lock = "Phone Locked"
                    last_usage = calculate_duration(prompt_time, closest_time)
                else:
                    phone_lock = np.nan
                    last_usage = np.nan
            else:
                if phone_event == "KEYGUARD_HIDDEN":
                    phone_lock = "Phone Locked"
                    last_usage = np.nan
                elif phone_event == "KEYGUARD_SHOWN":
                    phone_lock = "Phone Unlocked"
                    last_usage = 0
                else:
                    phone_lock = np.nan
                    last_usage = np.nan

            # print("==   {}".format(phone_lock))

        matched_phone_lock_list.append(phone_lock)
        matched_last_usage_list.append(last_usage)


    return matched_phone_lock_list, matched_last_usage_list


def transform(phone_lock_column):
    # return [1 if x >= 15 else 0 for x in phone_lock_column]
    return phone_lock_column


def create_column(prompt_local_datetime_series, intermediate_participant_path, date_in_study):
    print("\n> start generating the feature: phone screen lock ")

    # Read, parse and combine related intermediate file
    df_logs_combined = combine_intermediate_file(intermediate_participant_path, date_in_study)

    if df_logs_combined.shape[0] > 0:
        # Match the combined parsed intermediate file with prompt feature data frame
        phone_lock_column, last_usage_column  = match_feature(prompt_local_datetime_series, df_logs_combined)
    else:
        phone_lock_column = ["NF"] * len(prompt_local_datetime_series)
        last_usage_column = ["NF"] * len(prompt_local_datetime_series)

    # transform feature
    # result_column_transformed = transform(result_column)
    print("     --- success")

    return phone_lock_column, last_usage_column
