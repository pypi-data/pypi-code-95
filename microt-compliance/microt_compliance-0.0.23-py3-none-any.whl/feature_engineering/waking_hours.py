import pandas as pd
import numpy as np
from tqdm import tqdm
from datetime import timedelta
import datetime


def match_feature(prompt_feature_df, df_system_combined):
    print("     --- start transformation\n")
    # converter = lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f")
    # prompt_feature_datetime = pd.Series(map(converter, prompt_feature_df['PROMPT_LOCAL_TIME']))
    prompt_feature_df['PROMPT_Hour'] = [int(x.split(' ')[1].split(':')[0]) for x in prompt_feature_df['PROMPT_LOCAL_TIME']]
    promt_date_string = [x.split(" ")[0] for x in prompt_feature_df['PROMPT_LOCAL_TIME']]
    prompt_feature_df['PROMPT_Date'] = [datetime.strptime(x, '%Y-%m-%d').date() for x in promt_date_string]

    df_system_combined = df_system_combined.dropna(subset=['date'])
    df_system_combined.reset_index(inplace=True, drop=True)
    df_system_combined["LOG_TIMESTAMP"] = [datetime.strptime(x, '%m/%d/%Y') for x in df_system_combined['date']]
    df_system_combined['Date'] = df_system_combined['LOG_TIMESTAMP'].dt.date

    print("     --- start matching\n")
    matched_waking_hours_list = []
    matched_sleep_hours_list = []
    for idx in tqdm(prompt_feature_df.index):
        p_id = prompt_feature_df['Participant_ID'][idx]
        prompt_hour = prompt_feature_df['PROMPT_Hour'][idx]
        # print(prompt_hour)

        if prompt_hour > 4:
            prompt_date = prompt_feature_df['PROMPT_Date'][idx]
        else:
            prompt_date = prompt_feature_df['PROMPT_Date'][idx] - timedelta(days=1)

        df_system_participant = df_system_combined[df_system_combined['participant_ID'] == p_id][
            df_system_combined['Date'] == prompt_date]

        if df_system_participant.shape[0] == 0:
            waking_hour = np.nan
            sleep_hour = np.nan
            print("No wake and sleep hour found for {}".format(prompt_date))
        else:
            waking_hour = list(df_system_participant["current_wake_time"])[0]
            sleep_hour = list(df_system_participant["current_sleep_time"])[0]

        matched_waking_hours_list.append(waking_hour)
        matched_sleep_hours_list.append(sleep_hour)

    return matched_waking_hours_list, matched_sleep_hours_list


def transform(waking_hours_column):
    # return [1 if x >= 15 else 0 for x in waking_hours_column]
    return waking_hours_column


def create_column(prompt_feature_df, intermediate_root_path, feature_save_path, start_date, end_date):
    print("\n> start generating the feature: screen status ")
    participants_ids = prompt_feature_df['Participant_ID'].unique()

    # Read, parse and combine related intermediate file
    df_combined = pd.read_csv("/mnt/e/compliance_analysis/report/combined_report.csv")

    # Match the combined parsed intermediate file with prompt feature data frame
    waking_hours_column, sleep_hours_column = match_feature(prompt_feature_df, df_combined)


    return waking_hours_column, sleep_hours_column
