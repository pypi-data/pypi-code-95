import numpy as np

def create_column(feature_df, home_coordinates_dict):
    print("\n> start generating the feature: home location ")

    participants_id = feature_df['Participant_ID'].unique()
    home_list = []
    for p_id in participants_id:
        subset_df = feature_df[feature_df['Participant_ID'] == p_id]
        subset_df.reset_index(inplace=True, drop=True)

        boarder_coordinates = home_coordinates_dict[p_id]
        home_max_lat = boarder_coordinates[1]
        home_min_lat = boarder_coordinates[0]
        home_max_long = boarder_coordinates[3]
        home_min_long = boarder_coordinates[2]

        for idx in subset_df.index:
            coordinates_str = subset_df['location'][idx]
            # print(coordinates_str)
            if type(coordinates_str) != str:
                home = 0
                home_list.append(home)
                continue
            else:
                coordinates = coordinates_str.strip('][').split(', ')

                lat = float(coordinates[0])
                long = float(coordinates[1])
                home = 0

                if lat <= home_max_lat and lat >= home_min_lat and long <= home_max_long and long >= home_min_long:
                    home = 1

                home_list.append(home)
    return home_list
