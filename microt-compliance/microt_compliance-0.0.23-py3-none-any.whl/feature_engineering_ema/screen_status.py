import os
from os import sep
from glob import glob
import pandas as pd
import numpy as np
# from tqdm import tqdm
from datetime import datetime, timedelta
from microt_compliance_matrix import utils


target_file_pattern = 'phone_system_events_clean*.csv'

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
            raise Exception("pandas.errors.EmptyDataError (screen_status) : " + csv_path)
        except pd.errors.ParseError:
            raise Exception("pandas.errors.ParseError (screen_status) : " + csv_path)

        if df_day.shape[0] > 0:
            df_day['Participant_ID'] = [participant_id] * df_day.shape[0]
            df_logs_combined = pd.concat([df_logs_combined, df_day])

    # filter out irrelevant logs
    df_logs_combined = df_logs_combined[df_logs_combined['PHONE_EVENT'].isin(["PHONE_SCREEN_ON","PHONE_SCREEN_OFF"])]
    df_logs_combined.reset_index(inplace=True, drop=True)

    converter = lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f")
    df_logs_combined = df_logs_combined.dropna(subset=['LOG_TIME'])
    df_logs_combined.reset_index(inplace=True, drop=True)
    df_logs_combined["LOG_TIME"] = [x.split(" ")[0] + " " + x.split(" ")[1] for x in
                                         list(df_logs_combined["LOG_TIME"])]

    df_logs_combined['LOG_TIME_DATETIME'] = pd.Series(map(converter, df_logs_combined["LOG_TIME"]))
    if df_logs_combined.shape[0] > 0:
        df_logs_combined['Date'] = df_logs_combined['LOG_TIME_DATETIME'].dt.date

    return df_logs_combined


# def find_closest_time(prompt_time, subset_time_list):
#     i = bisect.bisect_left(subset_time_list, prompt_time)
#     closet_time = min(subset_time_list[max(0, i - 1): i + 2], key=lambda t: abs(prompt_time - t))
#     return closet_time
def find_prev_closest_time(prompt_time, subset_time_series):
    previous_timestamps = subset_time_series[subset_time_series < prompt_time]
    reverse = False
    if len(previous_timestamps) > 0:
        closet_time = previous_timestamps.max()
    else:
        after_timestamps = subset_time_series[subset_time_series > prompt_time]
        closet_time = after_timestamps.min()
        reverse = True
    return closet_time, reverse


def match_feature(prompt_local_datetime_series, df_logs_combined):
    print("     --- start matching")
    matched_result_list = []

    for idx in prompt_local_datetime_series.index:
        prompt_time = prompt_local_datetime_series[idx]
        # prompt_date = prompt_time.date()


        if df_logs_combined.shape[0] == 0:
            location = np.nan
        else:
            subset_time_series = df_logs_combined["LOG_TIME_DATETIME"]

            closest_time, reverse = find_prev_closest_time(prompt_time, subset_time_series)

            screen_event = list(df_logs_combined[df_logs_combined['LOG_TIME_DATETIME'] == closest_time][
                                     "PHONE_EVENT"])[0]

            # to determine screen on/off
            if not reverse:
                if screen_event == "PHONE_SCREEN_ON":
                    screen_status = "Screen On"
                elif screen_event == "PHONE_SCREEN_OFF":
                    screen_status = "Screen Off"
                else:
                    screen_status = np.nan
            else:
                if screen_event == "PHONE_SCREEN_ON":
                    screen_status = "Screen Off"
                elif screen_event == "PHONE_SCREEN_OFF":
                    screen_status = "Screen On"
                else:
                    screen_status = np.nan


        matched_result_list.append(screen_status)

    return matched_result_list


def transform(screen_status_column):
    # return [1 if x >= 15 else 0 for x in screen_status_column]
    return screen_status_column


def create_column(prompt_local_datetime_series, intermediate_participant_path, date_in_study):
    print("\n> start generating the feature: Screen status ")

    # Read, parse and combine related intermediate file
    df_logs_combined = combine_intermediate_file(intermediate_participant_path, date_in_study)

    if df_logs_combined.shape[0] > 0:
        # Match the combined parsed intermediate file with prompt feature data frame
        result_column = match_feature(prompt_local_datetime_series, df_logs_combined)
    else:
        result_column = ["NF"] * len(prompt_local_datetime_series)

    # transform feature
    result_column_transformed = transform(result_column)
    print("     --- success")

    return result_column_transformed
