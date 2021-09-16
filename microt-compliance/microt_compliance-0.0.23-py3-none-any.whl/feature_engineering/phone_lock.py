from os import path, sep, makedirs
from glob import glob
import pandas as pd
import numpy as np
from datetime import timedelta
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
            csv_path_list = sorted(glob(os.path.join(date_folder_path, 'phone_app_usage_clean*.csv')))  # file name
            if len(csv_path_list) == 0:
                print("No app usage daily file on {}".format(date))
                continue

            csv_path = csv_path_list[0]
            try:
                df_daily = pd.read_csv(csv_path)
            except:
                print("{} has null file".format(date))
                continue

            if df_daily.shape[0] > 0:
                df_daily['PARTICIPANT_ID'] = [p_id] * df_daily.shape[0]
                df_combined = pd.concat([df_combined, df_daily])

    # # remove error line
    # df_combined = df_combined[df_combined['phone_lock'] != "phone_lock"]
    try:
        df_combined = df_combined[df_combined.APP_EVENT.isin(["KEYGUARD_HIDDEN", "KEYGUARD_SHOWN"])]
    except:
        print("+++++++++++++++++++++++++++")
        print(participants_ids)
        print("+++++++++++++++++++++++++++")
    df_combined.reset_index(inplace=True, drop=True)
    # save a copy of combined file in compliance anaysis folder
    save_path = feature_save_path + sep + "compliance_analysis"  + sep + "uEMA_plus" + sep + "phone_lock"
    if df_combined.shape[0] > 0:
        if not path.exists(save_path):
            makedirs(save_path)

        df_combined.to_csv(save_path + sep + "combined.csv", index=False)

    return df_combined


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


def match_feature(prompt_feature_df, df_system_combined):
    print("     --- start transformation\n")
    converter = lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f")
    prompt_feature_df['PROMPT_TIMESTAMP'] = list(map(converter, prompt_feature_df['PROMPT_LOCAL_TIME']))
    # try:
    df_system_combined = df_system_combined.dropna(subset=['EVENT_TIME'])
    df_system_combined = df_system_combined[df_system_combined["EVENT_TIME"] != "unknown time"]
    df_system_combined.reset_index(inplace=True, drop=True)

    df_system_combined["EVENT_TIME"] = [x.strip(x.split(' ')[2]).strip(" ") for x in
                                         list(df_system_combined["EVENT_TIME"])]
    df_system_combined['EVENT_TIMESTAMP_LOCAL'] = pd.Series(map(converter, df_system_combined["EVENT_TIME"]))
    df_system_combined['Date'] = [x.date() for x in df_system_combined['EVENT_TIMESTAMP_LOCAL']]
    # except:
    #     print(prompt_feature_df.Participant_ID)
    #     print(df_system_combined.head())
    #     converter = lambda x: datetime.fromtimestamp(x/1000)-timedelta(hours=3)
    #     df_system_combined['EVENT_TIMESTAMP_LOCAL'] = pd.Series(map(converter, df_system_combined["EVENT_TIMESTAMP"]))
    #     df_system_combined['Date'] = df_system_combined['EVENT_TIMESTAMP_LOCAL'].dt.date

    print("     --- start matching\n")
    matched_phone_lock_list = []
    matched_last_usage_list = []
    for idx in tqdm(prompt_feature_df.index):
        p_id = prompt_feature_df['Participant_ID'][idx]
        prompt_time = prompt_feature_df['PROMPT_TIMESTAMP'][idx]
        prompt_date = prompt_time.date()

        df_system_participant = df_system_combined[df_system_combined['PARTICIPANT_ID'] == p_id][
            df_system_combined['Date'].isin([prompt_date-timedelta(1), prompt_date, prompt_date+timedelta(1)])]
        # only keep phone on and off events
        df_system_participant = df_system_participant[df_system_participant.APP_EVENT.isin(["KEYGUARD_HIDDEN", "KEYGUARD_SHOWN"])]

        last_usage = None
        if df_system_participant.shape[0] == 0:
            phone_lock = np.nan
            print("No phone events found")
        else:
            # print(df_system_participant["START_TIMESTAMP"][df_system_participant.shape[0]-20])
            subset_time_list = np.array(df_system_participant["EVENT_TIMESTAMP_LOCAL"])

            closest_time, reverse = find_prev_closest_time(prompt_time, subset_time_list)

            phone_event = list(df_system_participant[df_system_participant['EVENT_TIMESTAMP_LOCAL'] == closest_time][
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
                    phone_lock = np.nan
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


def create_column(prompt_feature_df, intermediate_root_path, feature_save_path, start_date, end_date):
    print("\n> start generating the feature: phone screen lock ")
    participants_ids = prompt_feature_df['Participant_ID'].unique()

    # Read, parse and combine related intermediate file
    df_combined = combine_intermediate_file(participants_ids, intermediate_root_path, feature_save_path, start_date,
                                            end_date)
    # df_combined = pd.read_csv(r"E:\compliance_analysis\phone_lock\combined.csv")
    # Match the combined parsed intermediate file with prompt feature data frame
    phone_lock_column, last_usage_column = match_feature(prompt_feature_df, df_combined)

    # transform feature
    phone_lock_column_transformed = transform(phone_lock_column)

    return phone_lock_column_transformed, last_usage_column
