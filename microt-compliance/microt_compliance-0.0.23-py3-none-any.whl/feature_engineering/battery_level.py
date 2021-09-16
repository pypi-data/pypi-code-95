from os import path, sep, makedirs
from glob import glob
import pandas as pd
import numpy as np
import bisect
from tqdm import tqdm
from microt_compliance_matrix.utils.validate_date import *


def combine_intermediate_file(participants_ids, intermediate_root_path, feature_save_path, start_date, end_date):
    df_combined = pd.DataFrame()
    for p_id in participants_ids:
        print("\n", p_id)
        participant_logs_path = intermediate_root_path + sep + "intermediate_file" + sep + p_id

        # step 1: generate date range where date folder exists (sharable code in utils)
        validated_date_list = validate_date(participant_logs_path, start_date, end_date)
        if len(validated_date_list) == 0:
            print("Cannot find date folder in data source between {} and {}".format(start_date, end_date))
            return None

        for date in validated_date_list:
            date_folder_path = participant_logs_path + sep + date
            csv_path_list = sorted(glob(os.path.join(date_folder_path, 'watch_battery_clean*.csv')))  # file name
            if len(csv_path_list) == 0:
                print("No battery daily file on {}".format(date))
                continue

            csv_path = csv_path_list[0]
            df_daily = pd.read_csv(csv_path)
            if df_daily.shape[0] > 0:
                df_daily['Participant_ID'] = [p_id] * df_daily.shape[0]
                df_combined = pd.concat([df_combined, df_daily])

    # remove error line
    df_combined = df_combined[df_combined['BATTERY_LEVEL'] != "BATTERY_LEVEL"]

    # save a copy of combined file in compliance anaysis folder
    save_path = feature_save_path + sep + "compliance_analysis" + sep + "uEMA_plus" + sep + "battery_level"
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


def match_feature(prompt_feature_df, df_battery_combined):
    print("     --- start transformation\n")
    converter = lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f")
    prompt_feature_df['PROMPT_TIMESTAMP'] = pd.Series(map(converter, prompt_feature_df['PROMPT_LOCAL_TIME']))
    df_battery_combined["START_TIME"] = [x.strip(x.split(' ')[2]).strip(" ") for x in list(df_battery_combined["START_TIME"])]
    # df_battery_combined.to_csv(r"E:\compliance_analysis\battery_level\waht.csv")
    # converter2 = lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
    df_battery_combined['START_TIMESTAMP'] = pd.Series(map(converter, df_battery_combined["START_TIME"]))
    df_battery_combined['Date'] = df_battery_combined['START_TIMESTAMP'].dt.date

    print("     --- start matching\n")
    matched_battery_level_list = []
    matched_charging_status_list = []
    for idx in tqdm(prompt_feature_df.index):
        p_id = prompt_feature_df['Participant_ID'][idx]
        prompt_time = prompt_feature_df['PROMPT_TIMESTAMP'][idx]
        prompt_date = prompt_time.date()

        df_battery_participant = df_battery_combined[df_battery_combined['Participant_ID'] == p_id][df_battery_combined['Date'] == prompt_date]
        if df_battery_participant.shape[0] == 0:
            battery_level = np.nan
            charging_status = np.nan
        else:
            # print(df_battery_participant["START_TIMESTAMP"][df_battery_participant.shape[0]-20])
            subset_time_list = list(df_battery_participant["START_TIMESTAMP"])

            closest_time = find_closest_time(prompt_time, subset_time_list)

            battery_level = list(df_battery_participant[df_battery_participant['START_TIMESTAMP'] == closest_time][
                "BATTERY_LEVEL"])[0]
            charging_status = list(df_battery_participant[df_battery_participant['START_TIMESTAMP'] == closest_time][
                "BATTERY_CHARGING"])[0]

        matched_battery_level_list.append(battery_level)
        matched_charging_status_list.append(charging_status)

    return matched_battery_level_list, matched_charging_status_list


def transform(battery_level_column):
    # return [1 if x >= 15 else 0 for x in battery_level_column]
    return battery_level_column


def create_column(prompt_feature_df, intermediate_root_path, feature_save_path, start_date, end_date):
    print("\n> start generating the feature: battery level ")
    participants_ids = prompt_feature_df['Participant_ID'].unique()

    # Read, parse and combine related intermediate file
    df_combined = combine_intermediate_file(participants_ids, intermediate_root_path, feature_save_path, start_date,
                                            end_date)
    # df_combined = pd.read_csv(r"E:\compliance_analysis\battery_level\combined.csv")
    # Match the combined parsed intermediate file with prompt feature data frame
    battery_level_column, charging_status_column = match_feature(prompt_feature_df, df_combined)

    # transform feature
    battery_level_column_transformed = transform(battery_level_column)

    return battery_level_column_transformed, charging_status_column
