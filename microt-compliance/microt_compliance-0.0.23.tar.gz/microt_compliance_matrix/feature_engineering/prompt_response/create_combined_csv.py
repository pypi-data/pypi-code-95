from .preprocess_promptResponse_raw import *
from .combine_appended_response import *


def create_combined_csv_file(participant_ids, intermediate_root_path, feature_save_path, start_date, end_date):
    for p_id in participant_ids:
        print("Now processing PromptResponse.csv file for {}".format(p_id))
        create_temporary_appended_response_files(p_id, intermediate_root_path, feature_save_path, start_date, end_date)

    df_prompt = combine_appended_response_for_all_participants(participant_ids, feature_save_path)
    return df_prompt
