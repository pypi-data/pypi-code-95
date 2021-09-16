"""
Functionality: This is the main script to generate a matrix of features of interest.

Arguments:
1) intermediate_participant_path
e.g., G:\...\intermediate_file\sharpnessnextpouch@timestudy_com

2) output_dir_path
e.g., C:\...\output_folder

3) date_in_study
e.g., 2021-01-01

4) decryption_password
eg., passwordpassword

Command line example:
python main.py [intermediate_participant_path] [output_dir_path] [date_in_study] [decryption_password]

Output: feature_mx_<date>.csv file that contains all features in the <output_dir_path> folder .
"""
import sys
import time
import os
from microt_compliance_matrix import utils
from microt_compliance_matrix import feature_engineering_ema


def compute_features_phone(intermediate_participant_path, output_dir_path, date_in_study, decryption_password):
    # Switch
    print_stats = False

    # Extract participant id from participant folder path
    participant_id = utils.extract_participant_id.extract_participant_id(intermediate_participant_path)

    # Create output folder
    output_participant_path = os.path.join(output_dir_path, participant_id)
    if not os.path.exists(output_participant_path):
        try:
            os.makedirs(output_participant_path)
        except FileExistsError:
            pass

    # Parse prompt response file for the specific date
    df_prompt = feature_engineering_ema.prompt_response.preprocess_promptResponse_raw.clean_response_files(
        intermediate_participant_path, date_in_study, participant_id)


    # - Outcome variable: completion status
    completion_status_binary = feature_engineering_ema.compliance.create_column(df_prompt['Answer_Status'],
                                                                                    print_stats)
    # - Feature matrix
    feature_df = df_prompt
    feature_df['Answer_Status'] = completion_status_binary

    # - Loading Participants Information
    info_dict = utils.load_participant_study_info.execute(intermediate_participant_path, output_dir_path)

    # - feature 1: Day of the week
    feature1 = feature_engineering_ema.day_of_the_week.create_column(df_prompt['Prompt_Local_DateTime'], print_stats)
    feature_df['DAY_OF_THE_WEEK'] = feature1
    # - feature 2: Time of the day
    feature2 = feature_engineering_ema.time_of_the_day.create_column(df_prompt['Prompt_Local_DateTime'], print_stats)
    feature_df['TIME_OF_THE_DAY'] = feature2
    # - feature 3: Days in the study
    feature3 = feature_engineering_ema.days_in_study.create_column(df_prompt, info_dict, print_stats)
    feature_df['DAYS_IN_THE_STUDY'] = feature3


    # - feature 4: battery level
    feature5, feature6 = feature_engineering_ema.battery_level.create_column(df_prompt['Prompt_Local_DateTime'], intermediate_participant_path, date_in_study)
    feature_df['BATTERY_LEVEL'] = feature5
    feature_df['CHARGING_STATUS'] = feature6

    # - feature 5: GPS location
    feature7 = feature_engineering_ema.location.create_column(df_prompt['Prompt_Local_DateTime'], intermediate_participant_path, date_in_study, decryption_password)
    feature_df['LOCATION'] = feature7

    # - feature 6: Location related

    # - feature 7: Screen Status
    feature9 = feature_engineering_ema.screen_status.create_column(df_prompt['Prompt_Local_DateTime'], intermediate_participant_path, date_in_study)
    feature_df['SCREEN_STATUS'] = feature9

    # - feature 10&11: wake and sleep hour
    feature10, feature11 = feature_engineering_ema.waking_hours.create_column(df_prompt['Prompt_Local_DateTime'], intermediate_participant_path, date_in_study)
    feature_df['WAKE_TIME'] = feature10
    feature_df['SLEEP_TIME'] = feature11

    # - feature 12: Phone lock status
    feature12, feature13 = feature_engineering_ema.phone_lock.create_column(df_prompt['Prompt_Local_DateTime'], intermediate_participant_path, date_in_study)
    feature_df['PHONE_LOCK'] = feature12
    feature_df['LAST_USAGE_DURATION'] = feature13

    csv_file_name = "feature_mx_{}".format(date_in_study) + ".csv"
    csv_save_path = os.path.join(output_dir_path, participant_id, csv_file_name)
    feature_df.to_csv(csv_save_path, index=False)

    return


if __name__ == "__main__":
    start = time.time()
    intermediate_participant_path = sys.argv[1]
    output_dir_path = sys.argv[2]
    date_in_study = sys.argv[3]
    decryption_password = sys.argv[4]

    compute_features_phone(intermediate_participant_path, output_dir_path, date_in_study, decryption_password)
    end = time.time()
    print("Finished\n")
    print("Runtime : {} seconds".format(round(end - start,2)))
