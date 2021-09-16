"""
Output: 1) a list of targeted features for the participant 2) print stats of the targeted features for the participant
e.g., [6,6,6,0,0,0,1,1,1]
"""

from datetime import datetime
from collections import Counter


def print_stats_single_column(feature_name, data):
    print('--------- Stats of Feature: ' + feature_name + ' ---------')
    counter = Counter(data)
    print(sorted(counter.items()))


def create_column(prompt_timestamp_column, print_stats=True):
    print("\n> start generating the feature: day of the week ")
    # map from timestamp to date object
    converter = lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f")
    prompt_dateobject_column = list(map(converter, prompt_timestamp_column))
    # prompt_dateobject_column = list(map(lambda x: datetime.fromtimestamp(x / 1000.0), prompt_timestamp_column))
    # map from date object to weekday
    prompt_weekday_column = list(map(lambda x: x.weekday(), prompt_dateobject_column))

    if print_stats == True:
        print_stats_single_column("weekday", prompt_weekday_column)

    return prompt_weekday_column
