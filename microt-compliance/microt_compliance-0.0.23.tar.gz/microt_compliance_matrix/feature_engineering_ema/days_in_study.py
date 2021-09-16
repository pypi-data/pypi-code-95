"""
Output: 1) a list of targeted features for the participant 2) print stats of the targeted features for the participant
"""

from datetime import datetime



def calculate_daysInStudy(prompte_date, start_date):
    delta = prompte_date - start_date
    return delta

# def get_start_date_dict():
#     # change to your path of combined_report.csv
#     combined_report_path = r"E:\compliance_analysis\report\combined_report.csv"
#     df_report = pd.read_csv(combined_report_path)
#     participants_list = df_report['participant_ID'].unique()
#     date_format = '%m/%d/%Y'
#     start_date_dict = {}
#     for p_id in participants_list:
#         start_date_str = list(df_report[df_report['participant_ID'] == p_id]['start_date'])[0]
#         start_date = datetime.strptime(start_date_str, date_format).date()
#         start_date_dict[p_id] = start_date
#     return start_date_dict

def create_column(df_prompt_combined, info_dict, print_stats=True):
    print("\n> start generating the feature: days in study ")
    participant_id = df_prompt_combined['Participant_ID'][0]

    if participant_id not in info_dict:
        raise Exception("Don't find this participant in info json. Check if this participant has data, and delete Misc and rerun the code. ")
    else:
        if "start_date" in info_dict[participant_id]:
            start_date = info_dict[participant_id]["start_date"]
            start_date_dateobject = datetime.strptime(start_date, "%Y-%m-%d").date()
        else:
            raise Exception(
                "Don't find this participant in info json. Check if this participant has daily report, and delete Misc and rerun the code. ")


    prompt_dateobject_date_series = df_prompt_combined.Prompt_Local_DateTime.dt.date

    days_in_study = prompt_dateobject_date_series.apply(lambda x: calculate_daysInStudy(x, start_date_dateobject))

    return days_in_study
