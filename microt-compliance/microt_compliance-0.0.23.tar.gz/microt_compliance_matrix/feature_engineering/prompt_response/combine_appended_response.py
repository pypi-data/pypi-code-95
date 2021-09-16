"""
Functionality: combine all the csv file in appended_response directory for each participant into one single csv
 and save in the directory .../participant_id@timestudy_com/combined_responses.

Usage: This script is intended mainly to be called by uema_all_features_dataframe.py.

Input: 1). participant_ids, a list of participants' id 2). MICROT_PATH 3). start_date
e.g., [aditya4_internal, jixin_internal]

Output: one combined single csv file for each participant, with each row indicating a prompted question and response
e.g., aditya4_internal_uEMA_combined.csv in .../aditya4_internal@timestudy_com/combined_responses
"""

from os import listdir, path, sep, makedirs
import pandas as pd
from datetime import datetime

def combine_appended_response_for_all_participants(participant_ids, feature_save_path):
    df = pd.DataFrame()
    for p_id in participant_ids:
        print("\nNow Combining for :  ", p_id)
        p_folder_path = feature_save_path + sep + "compliance_analysis" + sep + "uEMA" + sep + "prompt_response" + sep + p_id
        if path.isdir(p_folder_path + sep + "appended_response"):

            paticipant_logs_path = p_folder_path + sep + "appended_response"
            all_csvs = listdir(paticipant_logs_path)
            if len(all_csvs) == 0:
                continue

            for appended_csv in all_csvs:
                df_temp = pd.read_csv(paticipant_logs_path + sep + appended_csv)
                if df_temp.shape[0] > 0:
                    df = pd.concat([df, df_temp])

    # remove error lines
    df = df[df["Prompt_Timestamp"] != -1]
    df.reset_index(drop=True, inplace=True)

    # save the combined csv file
    save_folder_path = feature_save_path + sep + "compliance_analysis"  + sep + "uEMA_plus" + sep + "prompt_response"
    if not path.isdir(save_folder_path):
        makedirs(save_folder_path)
    df.to_csv(save_folder_path + sep + "combined.csv", index=False)

    return df

