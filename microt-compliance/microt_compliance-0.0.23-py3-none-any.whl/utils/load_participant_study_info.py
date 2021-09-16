
import os
import json
import time
from glob import glob
import pandas as pd


def add_start_date(participants_folder_path_list, info_dict):
    for p_folder_path in participants_folder_path_list:
        participant_id = p_folder_path.split(os.sep)[-1]
        print(participant_id)
        info_dict[participant_id] = dict()
        for date_folder in os.listdir(p_folder_path):
            target_list = list(glob(os.path.join(p_folder_path, date_folder, "phone_watch_daily_report*")))
            if len(target_list) > 0:
                df_daily = pd.read_csv(target_list[0])
                start_date_list = df_daily['start_date'].unique()
                for start_date in start_date_list:
                    if type(start_date) == str: # str or nan
                        info_dict[participant_id]['start_date'] = start_date
                        print(start_date)
                        break
                else:
                    continue # only executed if the inner loop did NOT break
                break # only executed if the inner loop DID break
    return info_dict


def create_json(intermediate_participant_path, output_dir_path):
    print("Creating new participant info json.")
    info_dict = dict()
    misc_folder_name = "misc"
    information_dict_name = "info.json"
    folder_path = os.path.join(output_dir_path, misc_folder_name)
    information_dict_path = os.path.join(folder_path, information_dict_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    intermediate_folder_path = os.path.abspath(os.path.join(intermediate_participant_path, os.pardir))

    participants_folder_path_list = list(glob(os.path.join(intermediate_folder_path, "*@timestudy_com")))
    info_dict = add_start_date(participants_folder_path_list, info_dict)
    # dump json file
    with open(information_dict_path, 'w') as f:
        json.dump(info_dict, f)

    print("Creating new participant info json. (Done)")
    return info_dict


def execute(intermediate_participant_path, output_dir_path, rerun=False):

    misc_folder_name = "misc"
    information_dict_name = "info.json"
    folder_path = os.path.join(output_dir_path, misc_folder_name)
    information_dict_path = os.path.join(folder_path, information_dict_name)

    if rerun: # when the json needs to be updated
        info_dict = create_json(intermediate_participant_path, output_dir_path)
    else:
        # Load existing json file
        # if os.path.exists(information_dict_path):
        #     with open(information_dict_path) as f:
        #         info_dict = json.load(f)
        # else: # Create if info file doesn't exist
        #     info_dict = create_json(intermediate_participant_path, output_dir_path)
        with open(information_dict_path) as f:
            info_dict = json.load(f)

    return info_dict



if __name__ == "__main__":
    output_dir_path = r"C:\Users\jixin\Desktop\test_result\compliance"
    intermediate_participant_path = r"G:\preprocessed_cluster\intermediate_file\sharpnessnextpouch@timestudy_com"
    start = time.time()
    info_dict = execute(intermediate_participant_path, output_dir_path)
    end = time.time()
    print(info_dict)
    print("Runtime : {}".format(round(end-start, 2)))
