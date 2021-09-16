from os import path, sep, makedirs
from glob import glob
import pandas as pd
import numpy as np
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
            csv_path_list = sorted(glob(os.path.join(date_folder_path, 'phone_system_events_clean*.csv')))  # file name
            if len(csv_path_list) == 0:
                print("No system events daily file on {}".format(date))
                continue

            csv_path = csv_path_list[0]
            df_daily = pd.read_csv(csv_path)
            if df_daily.shape[0] > 0:
                df_daily['PARTICIPANT_ID'] = [p_id] * df_daily.shape[0]
                df_combined = pd.concat([df_combined, df_daily])

    # # remove error line
    # df_combined = df_combined[df_combined['screen_status'] != "screen_status"]

    # save a copy of combined file in compliance anaysis folder
    save_path = feature_save_path + sep + "compliance_analysis"  + sep + "uEMA_plus" + sep + "system_events"
    if df_combined.shape[0] > 0:
        if not path.exists(save_path):
            makedirs(save_path)
        df_combined.reset_index(inplace=True, drop=True)
        df_combined.to_csv(save_path + sep + "combined.csv", index=False)

    return df_combined


# def find_closest_time(prompt_time, subset_time_list):
#     i = bisect.bisect_left(subset_time_list, prompt_time)
#     closet_time = min(subset_time_list[max(0, i - 1): i + 2], key=lambda t: abs(prompt_time - t))
#     return closet_time
def find_closest_time(prompt_time, subset_time_list):
    previous_timestamps = subset_time_list[subset_time_list < prompt_time]
    reverse = False
    if len(previous_timestamps) > 0:
        closet_time = previous_timestamps.max()
    else:
        after_timestamps = subset_time_list[subset_time_list > prompt_time]
        closet_time = after_timestamps.min()
        reverse = True
    return closet_time, reverse


def match_feature(prompt_feature_df, df_system_combined):
    print("     --- start transformation\n")
    converter = lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f")
    prompt_feature_df['PROMPT_TIMESTAMP'] = list(map(converter, prompt_feature_df['PROMPT_LOCAL_TIME']))
    df_system_combined = df_system_combined.dropna(subset=['LOG_TIME'])
    df_system_combined.reset_index(inplace=True, drop=True)
    df_system_combined["LOG_TIME"] = [x.strip(x.split(' ')[2]).strip(" ") for x in
                                         list(df_system_combined["LOG_TIME"])]
    df_system_combined['LOG_TIMESTAMP'] = pd.Series(map(converter, df_system_combined["LOG_TIME"]))
    df_system_combined['Date'] = df_system_combined['LOG_TIMESTAMP'].dt.date

    print("     --- start matching\n")
    matched_screen_status_list = []
    for idx in tqdm(prompt_feature_df.index):
        p_id = prompt_feature_df['Participant_ID'][idx]
        prompt_time = prompt_feature_df['PROMPT_TIMESTAMP'][idx]
        prompt_date = prompt_time.date()

        df_system_participant = df_system_combined[df_system_combined['PARTICIPANT_ID'] == p_id][
            df_system_combined['Date'] == prompt_date]
        # only keep screen on and off events
        df_system_participant = df_system_participant[df_system_participant.PHONE_EVENT.isin(["PHONE_SCREEN_ON", "PHONE_SCREEN_OFF"])]

        if df_system_participant.shape[0] == 0:
            screen_status = np.nan
            print("No phone events found")
        else:
            # print(df_system_participant["START_TIMESTAMP"][df_system_participant.shape[0]-20])
            subset_time_list = np.array(df_system_participant["LOG_TIMESTAMP"])

            closest_time, reverse = find_closest_time(prompt_time, subset_time_list)

            screen_event = list(df_system_participant[df_system_participant['LOG_TIMESTAMP'] == closest_time][
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

            # print("==   {}".format(screen_status))

        matched_screen_status_list.append(screen_status)


    return matched_screen_status_list


def transform(screen_status_column):
    # return [1 if x >= 15 else 0 for x in screen_status_column]
    return screen_status_column


def create_column(prompt_feature_df, intermediate_root_path, feature_save_path, start_date, end_date):
    print("\n> start generating the feature: screen status ")
    participants_ids = prompt_feature_df['Participant_ID'].unique()

    # Read, parse and combine related intermediate file
    df_combined = combine_intermediate_file(participants_ids, intermediate_root_path, feature_save_path, start_date,
                                            end_date)
    # df_combined = pd.read_csv(r"E:\compliance_analysis\screen_status\combined.csv")
    # Match the combined parsed intermediate file with prompt feature data frame
    screen_status_column = match_feature(prompt_feature_df, df_combined)

    # transform feature
    screen_status_column_transformed = transform(screen_status_column)

    return screen_status_column_transformed
