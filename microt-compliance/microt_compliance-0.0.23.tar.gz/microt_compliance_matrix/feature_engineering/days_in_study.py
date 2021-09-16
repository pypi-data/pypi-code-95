"""
Output: 1) a list of targeted features for the participant 2) print stats of the targeted features for the participant
"""

from os import path, sep, listdir
import pandas as pd
from datetime import datetime
from collections import Counter


def print_stats_single_column(feature_name, data):
    print('--------- Stats of Feature: ' + feature_name + ' ---------')
    counter = Counter(data)
    print(sorted(counter.items()))


def calculate_daysInStudy(dateobject, start_date_dict, name):
    start_date = start_date_dict[name]
    delta = dateobject - start_date
    return delta

# def get_start_date_dict():
#     # change to your path of combined_report.csv
#     combined_report_path = r"E:\compliance_analysis\report\combined_report.csv"
#     df_report = pd.read_csv(combined_report_path)
#     participants_list = df_report['participant_ID'].unique()
#     date_format = '%Y-%m-%d'
#     start_date_dict = {}
#     for p_id in participants_list:
#         start_date_str = list(df_report[df_report['participant_ID'] == p_id]['start_date'])[0]
#         start_date = datetime.strptime(start_date_str, date_format).date()
#         start_date_dict[p_id] = start_date
#     return start_date_dict

def get_start_date_dict():
    # change to your path of combined_report.csv
    combined_report_path = r"E:\compliance_analysis\report\combined_report.csv"
    # combined_report_path = r"C:\Users\jixin\Desktop\missing\start_date_table.csv"
    df_report = pd.read_csv(combined_report_path)
    participants_list = df_report['participant_ID'].unique()
    date_format = '%m/%d/%Y'
    start_date_dict = {}
    for p_id in participants_list:
        start_date_str = list(df_report[df_report['participant_ID'] == p_id]['start_date'])[0]
        start_date = datetime.strptime(start_date_str, date_format).date()
        start_date_dict[p_id] = start_date
    return start_date_dict

def create_column(df_prompt_combined, print_stats=True):
    print("\n> start generating the feature: days in study ")
    # get the start date dictionary
    start_date_dict = get_start_date_dict()

    # map from timestamp to date object
    converter = lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f")
    prompt_dateobject_column = pd.Series(map(converter, df_prompt_combined['Prompt_Local_Time']))
    # prompt_dateobject_column = pd.Series(
    #     map(lambda x: datetime.fromtimestamp(x / 1000.0), df_prompt_combined['Prompt_Timestamp']))
    # get start_date dateobject
    df = pd.DataFrame(
        {"Participant_ID": list(df_prompt_combined['Participant_ID']), "Date": prompt_dateobject_column.dt.date})
    group_df = df.groupby("Participant_ID")
    time_in_study = group_df.apply(lambda x: calculate_daysInStudy(x.Date, start_date_dict, x.name))
    date_list = list(time_in_study.reset_index().sort_values(by=["level_1"])['Date'])
    days_in_study = [x.days for x in date_list]

    if print_stats == True:
        # print_stats_single_column("daysInStudy", prompt_daysInStudy_column)
        pass
    return days_in_study
