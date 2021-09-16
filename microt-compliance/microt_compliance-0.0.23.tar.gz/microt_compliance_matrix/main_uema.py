"""
Functionality: This is the main script to generate a matrix of features of interest.

Input:
1) intermediate root path
2) feature save path
3) participants included text file path
4) start_date (inclusive)
5) end_date (inclusive)
e.g., python main.py [intermediate_root_path] [feature_save_path] [participants_included_text_file_path] start_date end_date

Output: all_features.csv file that contains all features and is ready for modeling after import.
"""
import sys
import pandas as pd
from os import sep


def get_all_features(participant_ids, intermediate_root_path, feature_save_path, start_date, end_date, parallel_participant):
    # step1: parse and combine prompt response file for each participant
    df_prompt_combined = src.feature_engineering.prompt_response.create_combined_csv.create_combined_csv_file(
        participant_ids,
        intermediate_root_path,
        feature_save_path,
        start_date, end_date)

    # df_prompt_combined = pd.read_csv(r"F:\compliance_analysis\prompt_response\combined.csv")
    prompt_timestamp_column = df_prompt_combined['Prompt_Local_Time']
    # feature engineering related to prompt response file
    print_stats = False

    # - outcome: compliance
    compliance_binary = src.feature_engineering.compliance.create_column(df_prompt_combined['Completion_Status'],
                                                                         print_stats)
    # - feature 1: Day of the week
    feature1 = src.feature_engineering.day_of_the_week.create_column(prompt_timestamp_column, print_stats)
    # - feature 2: Time of the day
    feature2 = src.feature_engineering.time_of_the_day.create_column(prompt_timestamp_column, print_stats)
    # - feature 3: Days in the study
    feature3 = src.feature_engineering.days_in_study.create_column(df_prompt_combined, print_stats)

    # combine features
    prompt_feature_df = pd.DataFrame(
        list(zip(df_prompt_combined['Participant_ID'], df_prompt_combined['Prompt_Local_Time'], compliance_binary,
                 feature1, feature2, feature3)),
        columns=['Participant_ID', 'PROMPT_LOCAL_TIME', 'COMPLIANCE', 'DAY_OF_THE_WEEK', 'TIME_OF_THE_DAY',
                 'DAYS_IN_THE_STUDY'])

    feature_df = prompt_feature_df
    feature_df.to_csv(
        feature_save_path + sep + "compliance_analysis" + sep + "uEMA_plus" + sep + "feature_temp.csv", index=False)

    # # - feature 4: battery level
    # feature_df = pd.read_csv(r"F:\compliance_analysis\uEMA\feature_temp_uema2.csv")
    # feature_df = pd.read_csv("/mnt/f/compliance_analysis/uEMA/feature_temp_combined.csv")
    # feature_df = pd.read_csv("/mnt/e/compliance_analysis/uEMA/feature_wake_combined_type.csv")
    # feature_df = feature_df[feature_df.Participant_ID == parallel_participant]
    # if os.path.exists(feature_save_path + sep + "compliance_analysis" + sep + "uEMA" + sep + "feature_lock_" + parallel_participant + ".csv"):
    #     print("File exists for {}".format(parallel_participant))
    #     return

    # feature_df = feature_df[feature_df.Participant_ID == parallel_participant]
    # feature_df.reset_index(inplace=True, drop=True)
    # feature5, feature6 = feature_engineering.battery_level.create_column(feature_df, intermediate_root_path,
    #                                                            feature_save_path, start_date, end_date)
    # feature_df['battery_level'] = feature5
    # feature_df['charging_status'] = feature6
    #
    # feature_df.to_csv(
    #     feature_save_path + sep + "compliance_analysis" + sep + "uEMA" + sep + "feature_battery_" + parallel_participant + ".csv", index=False)

    # - feature 7: GPS location
    # feature7 = feature_engineering.location.create_column(feature_df, intermediate_root_path,
    #                                                       feature_save_path, start_date, end_date)
    # feature_df['location'] = feature7


    # # - feature 8: Home or other locations
    # # home_coordinates_dict = utils.home_coordinates.get_home_boarder_coordinates(participant_ids, intermediate_root_path)
    # # with open(feature_save_path + sep + "compliance_analysis" + sep + "location" + sep + "home_coord_dict.json", 'a') as fp:
    # #     json.dump(home_coordinates_dict, fp)
    # # with open(feature_save_path + sep + "compliance_analysis" + sep + "location" + sep + "home_coord_dict.json", 'rb') as fp:
    # #     home_coordinates_dict = json.load(fp)
    # # feature8 = feature_engineering.home_location.create_column(feature_df, home_coordinates_dict)
    # # feature_df['home'] = feature8
    # #
    # save file
    # feature_df.to_csv(
    #     feature_save_path + sep + "compliance_analysis" + sep + "uEMA" + sep + "feature_gps_" + parallel_participant + ".csv", index=False)
    # feature9 = feature_engineering.screen_status.create_column(feature_df, intermediate_root_path,
    #                                                       feature_save_path, start_date, end_date)
    # feature_df['screen_status'] = feature9
    #
    # feature_df.to_csv(
    #     feature_save_path + sep + "compliance_analysis" + sep + "uEMA" + sep + "feature_screen_" + parallel_participant + ".csv", index=False)

    # - feature 10&11: wake and sleep hour
    # feature10, feature11 = feature_engineering.waking_hours.create_column(feature_df, intermediate_root_path,
    #                                                       feature_save_path, start_date, end_date)
    # feature_df['wake_time'] = feature10
    # feature_df['sleep_time'] = feature11
    # - feature 12: Phone lock status
    # feature12, feature13 = feature_engineering.phone_lock.create_column(feature_df, intermediate_root_path,
    #                                                       feature_save_path, start_date, end_date)
    # feature_df['phone_lock'] = feature12
    # feature_df['last_usage'] = feature13
    #
    # feature_df.to_csv(
    #     feature_save_path + sep + "compliance_analysis" + sep + "uEMA" + sep + "feature_lock_" + parallel_participant + ".csv", index=False)

    return


if __name__ == "__main__":
    intermediate_root_path = sys.argv[1]
    feature_save_path = sys.argv[2]
    participant_text_file_path = sys.argv[3]
    start_date = sys.argv[4]
    end_date = sys.argv[5]
    parallel_participant = sys.argv[6]

    participant_ids = []
    # participant_ids = utils.parse_participants.parse_participants(participant_text_file_path)
    df = get_all_features(participant_ids, intermediate_root_path, feature_save_path, start_date, end_date, parallel_participant)
    # df.to_csv(feature_save_path + sep + "compliance_analysis" + sep + "all_features.csv", index=False)
    print("\nFinished")
