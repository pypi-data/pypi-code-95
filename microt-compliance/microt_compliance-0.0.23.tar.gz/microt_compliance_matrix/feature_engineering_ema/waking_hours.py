import os
from os import sep
from glob import glob
import pandas as pd
import numpy as np
# from tqdm import tqdm
from datetime import datetime, timedelta
from microt_compliance_matrix import utils

target_file_pattern = 'phone_watch_daily_report_clean*.csv'

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

        # # 1 day after target date
        # date_format = "%Y-%m-%d"
        # one_date_after_datetime = datetime.strptime(date_in_study, date_format).date() + timedelta(days=1)
        # one_date_after = one_date_after_datetime.strftime(date_format)
        # date_folder_path = intermediate_participant_path + sep + one_date_after
        # one_day_after_log_paths = sorted(glob(os.path.join(date_folder_path, target_file_pattern)))  # file name
        # if len(one_day_after_log_paths) != 0:
        #     validated_date_list.append(one_date_after)


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
        df_day = pd.read_csv(csv_path)
        if df_day.shape[0] > 0:
            df_day['Participant_ID'] = [participant_id] * df_day.shape[0]
            df_logs_combined = pd.concat([df_logs_combined, df_day])


    converter = lambda x: datetime.strptime(x, "%Y-%m-%d")
    df_logs_combined = df_logs_combined.dropna(subset=['date'])
    df_logs_combined.reset_index(inplace=True, drop=True)

    df_logs_combined['Date_Datetime'] = pd.Series(map(converter, df_logs_combined["date"]))
    df_logs_combined['Date'] = df_logs_combined['Date_Datetime'].dt.date

    return df_logs_combined


def match_feature(prompt_local_datetime_series, df_logs_combined):

    prompt_hour_list = [int(x.hour) for x in prompt_local_datetime_series]
    prompt_date_datetime_list = [x.date() for x in prompt_local_datetime_series]
    prompt_feature_df = pd.DataFrame({"Prompt_Hour": prompt_hour_list, "Prompt_Date_Datetime": prompt_date_datetime_list})

    print("     --- start matching\n")
    matched_waking_hours_list = []
    matched_sleep_hours_list = []
    for idx in prompt_feature_df.index:

        prompt_hour = prompt_feature_df['Prompt_Hour'][idx]
        # print(prompt_hour)

        if prompt_hour > 4:
            prompt_date = prompt_feature_df['Prompt_Date_Datetime'][idx]
        else:
            prompt_date = prompt_feature_df['Prompt_Date_Datetime'][idx] - timedelta(days=1)

        df_logs_combined = df_logs_combined[df_logs_combined['Date'] == prompt_date]

        if df_logs_combined.shape[0] == 0:
            waking_hour = np.nan
            sleep_hour = np.nan
            print("No wake and sleep hour found for {}".format(prompt_date))
        else:
            waking_hour = list(df_logs_combined["current_wake_time"])[0]
            sleep_hour = list(df_logs_combined["current_sleep_time"])[0]

        matched_waking_hours_list.append(waking_hour)
        matched_sleep_hours_list.append(sleep_hour)

    return matched_waking_hours_list, matched_sleep_hours_list


def transform(waking_hours_column):
    # return [1 if x >= 15 else 0 for x in waking_hours_column]
    return waking_hours_column


def create_column(prompt_local_datetime_series, intermediate_participant_path, date_in_study):
    print("\n> start generating the feature: Waking hours ")

    # Read, parse and combine related intermediate file
    df_logs_combined = combine_intermediate_file(intermediate_participant_path, date_in_study)

    if df_logs_combined.shape[0] > 0:
        # Match the combined parsed intermediate file with prompt feature data frame
        waking_hours_column, sleep_hours_column = match_feature(prompt_local_datetime_series, df_logs_combined)
    else:
        waking_hours_column = ["NF"] * len(prompt_local_datetime_series)

    print("     --- success")


    return waking_hours_column, sleep_hours_column
