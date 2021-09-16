"""
Output: 1) a list of targeted features for the participant 2) print stats of the targeted features for the participant
"""

from os import path, sep
import pandas as pd
from datetime import datetime
from collections import Counter
import sys


def print_stats_single_column(feature_name, data):
    print('--------- Stats of Feature: ' + feature_name + ' ---------')
    counter = Counter(data)
    print(sorted(counter.items()))


def categorize_timeOfDay(dateobject):
    hour = dateobject.hour
    # TBD
    # if 4 < hour and hour < 12:
    #     return "morning"
    # elif hour > 12 and hour < 17:
    #     return "afternoon"
    # else:
    #     return "evening/night"
    return hour

def create_column(prompt_timestamp_column, print_stats=True):
    print("\n> start generating the feature: time of the day")
    # map from timestamp to date object
    converter = lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f")
    prompt_dateobject_column = pd.Series(map(converter, prompt_timestamp_column))
    # prompt_dateobject_column = list(map(lambda x: datetime.fromtimestamp(x / 1000.0), prompt_timestamp_column))
    # map from date object to weekday
    prompt_timeOfDay_column = list(map(lambda x: categorize_timeOfDay(x), prompt_dateobject_column))

    if print_stats == True:
        print_stats_single_column("timeOfDay", prompt_timeOfDay_column)

    return prompt_timeOfDay_column

