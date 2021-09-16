"""
Functionality: Parse the content of .../logs-watch/PromptResponses.log.csv for individual participant into formatted
matrices day by day and save as csv file in the directory .../participant_id@timestudy_com/appended_response.

Usage: This script is intended mainly to be called by uema_all_features_dataframe.py.

Input: python preprocess_promptResponse_raw.py [PARTICIPANT_ID] [microT_root_path] [start_date]
e.g., python preprocess_promptResponse_raw.py aditya4_internal .../MICROT 2020-01-01

Output: csv file for each day of the participant, with each row indicating a prompted question and response
e.g., aditya4_internal_uEMA_****-**-**.csv in .../aditya4_internal@timestudy_com/appended_response
"""
import os
import sys

import pandas.errors

from microt_compliance_matrix.utils.convert_timestamp import *
from glob import glob

columns_list = ["Prompt_Type", "Study_Mode", "Initial_Prompt_Local_Time", "Initial_Prompt_UnixTime",
                "Initial_Prompt_UTC_Offset ",
                "Answer_Status", 'Question_Set_Completion_Local_Time', 'Question_Set_Completion_UnixTime',
                'Reprompt1_Prompt_Date',
                'Reprompt1_Prompt_Local_Time', 'Reprompt1_Prompt_UnixTime',
                'Reprompt2_Prompt_Date', 'Reprompt2_Prompt_Local_Time',
                'Reprompt2_Prompt_UnixTime ', 'Reprompt3_Prompt_Date',
                'Reprompt3_Prompt_Local_Time', 'Reprompt3_Prompt_UnixTime',
                'Reprompt4_Prompt_Date', 'Reprompt4_Prompt_Local_Time',
                'Reprompt4_Prompt_UnixTime', 'Reprompt5_Prompt_Date',
                'Reprompt5_Prompt_Local_Time', 'Reprompt5_Prompt_UnixTime']

prompt_type_excluded = ['None_Sleep', 'None_Empty']


def extract_reprompt(df_pr_phone):
    prompt_arrays = []
    for idx in df_pr_phone.index:
        row = df_pr_phone.loc[idx]
        # How it works: for status repeated for both init prompt and reprompts, add the label to all prompts;
        # for completed prompts, label "neverStarted" to the prompts before the last one.
        if row["Answer_Status"] in ["NeverStarted", "Started", "NeverPrompted"]:
            # non-completed

            # init prompt
            new_reprompt_row = []
            new_reprompt_row += list(row[['Prompt_Type', 'Study_Mode']])
            new_reprompt_row.append(row["Initial_Prompt_Local_Time"])
            new_reprompt_row.append(row["Answer_Status"])
            new_reprompt_row.append(row["Initial_Prompt_Local_Time"])
            new_reprompt_row.append(row["Initial_Prompt_UTC_Offset "])
            prompt_arrays.append(new_reprompt_row)

            # reprompt
            for i in range(1, 6):
                reprompt_num = "Reprompt" + str(i)
                reprompt_unix = reprompt_num + "_Prompt_UnixTime"
                reprompt_local = reprompt_num + "_Prompt_Local_Time"
                if row[reprompt_unix] == -1:
                    break
                else:
                    new_reprompt_row = []
                    new_reprompt_row += list(row[['Prompt_Type', 'Study_Mode']])
                    new_reprompt_row.append(row["Initial_Prompt_Local_Time"])
                    new_reprompt_row.append(row["Answer_Status"])
                    new_reprompt_row.append(row[reprompt_local])
                    new_reprompt_row.append(row["Initial_Prompt_UTC_Offset "])
                    prompt_arrays.append(new_reprompt_row)

        else:
            # completed
            for i in range(1, 6):
                reprompt_num = "Reprompt" + str(i)
                reprompt_unix = reprompt_num + "_Prompt_UnixTime"
                if row[reprompt_unix] == -1:
                    last_reprompt_num = i - 1
                    break

            if last_reprompt_num == 0:
                # init prompt
                new_reprompt_row = []
                new_reprompt_row += list(row[['Prompt_Type', 'Study_Mode']])
                new_reprompt_row.append(row["Initial_Prompt_Local_Time"])
                new_reprompt_row.append(row["Answer_Status"])
                new_reprompt_row.append(row["Initial_Prompt_Local_Time"])
                new_reprompt_row.append(row["Initial_Prompt_UTC_Offset "])
                prompt_arrays.append(new_reprompt_row)
                continue
            else:
                for i in range(0, last_reprompt_num + 1):

                    if i == 0:
                        status = "NeverStarted"
                        new_reprompt_row = []
                        new_reprompt_row += list(row[['Prompt_Type', 'Study_Mode']])
                        new_reprompt_row.append(row["Initial_Prompt_Local_Time"])
                        new_reprompt_row.append(status)
                        new_reprompt_row.append(row["Initial_Prompt_Local_Time"])
                        new_reprompt_row.append(row["Initial_Prompt_UTC_Offset "])
                        prompt_arrays.append(new_reprompt_row)

                    else:
                        if i == last_reprompt_num:
                            status = row["Answer_Status"]
                        else:
                            status = "NeverStarted"

                        reprompt_num = "Reprompt" + str(i)
                        reprompt_unix = reprompt_num + "_Prompt_UnixTime"
                        reprompt_local = reprompt_num + "_Prompt_Local_Time"

                        new_reprompt_row = []
                        new_reprompt_row += list(row[['Prompt_Type', 'Study_Mode']])
                        new_reprompt_row.append(row["Initial_Prompt_Local_Time"])
                        new_reprompt_row.append(status)
                        new_reprompt_row.append(row[reprompt_local])
                        new_reprompt_row.append(row["Initial_Prompt_UTC_Offset "])
                        prompt_arrays.append(new_reprompt_row)

    df_prompt = pd.DataFrame(prompt_arrays)
    if df_prompt.shape[0] > 0:
        df_prompt.columns = ['Prompt_Type', 'Study_Mode', 'Initial_Prompt_Local_Time', 'Answer_Status', 'Question_Set_Prompt_Local_Time', 'UTC_Offset']

    return df_prompt


def clean_response_files(intermediate_participant_path, date_in_study, participant_id):
    # Check if date folder exists
    date_folder_path = os.path.join(intermediate_participant_path, date_in_study)
    # date_exist = validate_date(date_folder_path)
    # if not date_exist:
    #     print("Cannot find date folder for {}".format(date_in_study))
    #     raise Exception("Cannot find date folder for {}".format(date_in_study))

    # Check if phone_promptresponse file exists for this date
    csv_path = list(glob(os.path.join(date_folder_path, 'phone_promptresponse_clean*.csv')))
    if len(csv_path) == 0:
        print(date_folder_path)
        print("No intermediate promptresponse csv file on {}".format(date_in_study))
        quit()

    # read and filter prompt type
    try:
        df_raw = pd.read_csv(csv_path[0])
    except pandas.errors.EmptyDataError:
        raise Exception("pandas.errors.EmptyDataError (prompt response) : " + csv_path[0])


    if df_raw.shape[0] == 0:
        print("Empty prompt response file : " + csv_path[0])
        quit()
    df_raw = df_raw[columns_list]

    if "Reprompt2_Prompt_UnixTime " in df_raw.columns:
        df_raw = df_raw.rename(columns={"Reprompt2_Prompt_UnixTime ": "Reprompt2_Prompt_UnixTime"})

    df_raw = df_raw[~df_raw.Prompt_Type.isin(prompt_type_excluded)]
    df_raw.reset_index(drop=True, inplace=True)

    # extract reprompts and treated them as separate prompts
    df_reprompt = extract_reprompt(df_raw)

    if df_reprompt.shape[0] == 0:
        print("Empty prompt response file after filtering : " + csv_path[0])
        quit()

    # add participant id column
    df_reprompt.insert(loc=0, column='Participant_ID', value=participant_id)

    # time zone processing
    df_reprompt.reset_index(drop=True, inplace=True)
    Prompt_Local_Time_list = []
    for idx in df_reprompt.index:
        prompt_local_time_timezone = df_reprompt['Question_Set_Prompt_Local_Time'][idx]
        prompt_local_time_timezone_split = prompt_local_time_timezone.split(" ")
        prompt_local_time_timezone_split_len = len(prompt_local_time_timezone_split)
        if prompt_local_time_timezone_split_len == 3:
            Prompt_Local_Time_list.append(prompt_local_time_timezone_split[0] + " " + prompt_local_time_timezone_split[1])
        else:
            print("Prompt response time zone error : " + intermediate_participant_path + "//" + date_in_study)
            Prompt_Local_Time_list.append(prompt_local_time_timezone)

    converter = lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
    prompt_dateobject_column = list(map(converter, Prompt_Local_Time_list))
    df_reprompt['Prompt_Local_DateTime'] = prompt_dateobject_column

    return df_reprompt


if __name__ == "__main__":
    p_id = sys.argv[1]
    intermediate_root_path = sys.argv[2]
    feature_save_path = sys.argv[3]
    start_date = sys.argv[4]
    end_date = sys.argv[5]
    clean_response_files(p_id, intermediate_root_path, feature_save_path, start_date, end_date)
