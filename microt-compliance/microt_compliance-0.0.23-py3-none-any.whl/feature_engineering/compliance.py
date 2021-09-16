"""
Output: a list of binary values of prompt compliance
e.g., [0,0,0,1,1,1]
"""

from collections import Counter

completion_list = ["Completed", "CompletedThenDismissed"]


def print_stats_single_column(feature_name, data):
    print('--------- Stats of Feature: ' + feature_name + ' ---------')
    counter = Counter(data)
    print(sorted(counter.items()))


def get_compliance_value(completion_str):

    value = 0
    if completion_str in completion_list:
        value = 1

    return value


def create_column(completion_status_column, print_stats=True):
    print("\n> start generating the feature: compliance ")
    prompt_compliance_column = list(map(lambda x: get_compliance_value(x), completion_status_column))

    if print_stats == True:
        print_stats_single_column("compliance", prompt_compliance_column)

    return prompt_compliance_column
