"""
Output: a list of categorical values indicating categories of study mode
e.g., [2,1,1,1,1]
"""

from collections import Counter


def print_stats_single_column(feature_name, data):
    print('--------- Stats of Feature: ' + feature_name + ' ---------')
    counter = Counter(data)
    print(sorted(counter.items()))


def get_mode_value(mode_str):
    value = 0
    if mode_str == "TIME":
        value = 1
    elif mode_str == "BURST":
        value = 2

    return value


def create_column(prompt_df, print_stats=True):
    study_mode_column = prompt_df['Study_Mode']
    study_mode_column = list(map(lambda x: get_mode_value(x), study_mode_column))

    if print_stats == True:
        print_stats_single_column("study mode", study_mode_column)

    return study_mode_column
