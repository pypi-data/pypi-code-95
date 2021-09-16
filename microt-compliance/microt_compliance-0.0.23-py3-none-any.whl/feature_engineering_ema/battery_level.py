import os
from os import sep
from glob import glob
import pandas as pd
import numpy as np
import bisect
from datetime import datetime, timedelta
from microt_compliance_matrix import utils

target_file_pattern = 'phone_battery_clean*.csv'


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

def clean_dataframe(df):
    df.reset_index(inplace=True, drop=True)
    dropped_rows = []
    for idx in df.index:
        local_time_str = df["Local_Time"][idx]
        if ('-1' in local_time_str) or len(local_time_str.split(' ')) > 3:
            dropped_rows.append(idx)
    df = df.drop(dropped_rows)

    df.reset_index(inplace=True, drop=True)
    return df

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
            raise Exception("pandas.errors.EmptyDataError (battery_level) : " + csv_path)

        if df_day.shape[0] > 0:
            df_day['Participant_ID'] = [participant_id] * df_day.shape[0]
            df_logs_combined = pd.concat([df_logs_combined, df_day])


    converter = lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f")
    df_logs_combined = df_logs_combined.dropna(subset=['Local_Time'])
    df_logs_combined = clean_dataframe(df_logs_combined)

    try:
        df_logs_combined["Local_Time"] = [x.split(" ")[0] + " " + x.split(" ")[1] for x in
                                          list(df_logs_combined["Local_Time"])]

        # converter2 = lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
        df_logs_combined['Local_Timestamp'] = pd.Series(map(converter, df_logs_combined["Local_Time"]))
        df_logs_combined['Date'] = df_logs_combined['Local_Timestamp'].dt.date
    except IndexError:
        raise Exception(
            "IndexError: list index out of range (battery_level) : " + intermediate_participant_path + sep + date_in_study + str(
                list(df_logs_combined["Local_Time"])))
    except Exception:
        raise Exception("Exception (battery_level) : " + intermediate_participant_path + sep + date_in_study)

    return df_logs_combined


def find_closest_time(prompt_time, subset_time_list):
    i = bisect.bisect_left(subset_time_list, prompt_time)
    closet_time = min(subset_time_list[max(0, i - 1): i + 2], key=lambda t: abs(prompt_time - t))
    return closet_time


def match_feature(prompt_local_datetime_series, df_logs_combined):
    print("     --- start matching")
    matched_battery_level_list = []
    matched_charging_status_list = []

    for idx in prompt_local_datetime_series.index:
        prompt_time = prompt_local_datetime_series[idx]
        # prompt_date = prompt_time.date()

        if df_logs_combined.shape[0] == 0:
            battery_level = np.nan
            charging_status = np.nan
        else:
            subset_time_list = list(df_logs_combined["Local_Timestamp"])

            closest_time = find_closest_time(prompt_time, subset_time_list)

            battery_level = list(df_logs_combined[df_logs_combined['Local_Timestamp'] == closest_time][
                                     "Percentage"])[0]
            charging_status = list(df_logs_combined[df_logs_combined['Local_Timestamp'] == closest_time][
                                       "isCharging"])[0]

        matched_battery_level_list.append(battery_level)
        matched_charging_status_list.append(charging_status)

    return matched_battery_level_list, matched_charging_status_list


def transform(battery_level_column):
    # return [1 if x >= 15 else 0 for x in battery_level_column]
    return battery_level_column


def create_column(prompt_local_datetime_series, intermediate_participant_path, date_in_study):
    print("\n> start generating the feature: battery level ")

    # Read, parse and combine related intermediate file
    df_logs_combined = combine_intermediate_file(intermediate_participant_path, date_in_study)

    if df_logs_combined.shape[0] > 0:
        # Match the combined parsed intermediate file with prompt feature data frame
        battery_level_column, charging_status_column = match_feature(prompt_local_datetime_series, df_logs_combined)
    else:
        battery_level_column = ["NF"] * len(prompt_local_datetime_series)
        charging_status_column = ["NF"] * len(prompt_local_datetime_series)

    # transform feature
    battery_level_column_transformed = transform(battery_level_column)
    print("     --- success")

    return battery_level_column_transformed, charging_status_column
