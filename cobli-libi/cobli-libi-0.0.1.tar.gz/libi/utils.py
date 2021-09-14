import time
from datetime import datetime, timedelta
from urllib.parse import urlencode

import pandas as pd
import requests

from libi.errors import RetrieveDataError

BASE_URL = 'https://api.cobli.co/'


def get_data(
        fleet_data: dict,
        resource_url: str,
        resource_url_query_params: dict,
        worksheet_index=0
) -> pd.DataFrame:
    """
    Return an unified pandas dataframe based on a given resource for specified fleets

    :param fleet_data: dict {'fleet_name': 'api_key'}
    :param resource_url: str - API resource endpoint url
    :param resource_url_query_params: dict - API resource query params
    :param worksheet_index: what worksheet to read (if applies)
    :return: pd.DataFrame
    """
    dataframe = pd.DataFrame()
    for fleet_name, api_key in fleet_data.items():
        _df = get_specific_data(fleet_name, api_key, resource_url, resource_url_query_params, worksheet_index)
        dataframe = dataframe.append(_df)
    return dataframe


def get_specific_data(
        fleet_name: str,
        api_key: str,
        resource_url: str,
        resource_url_query_params: dict,
        worksheet_index=0
) -> pd.DataFrame:
    """Return a specific pandas dataframe for a given resource of a specified fleet"""
    headers = {
        'Cobli-Api-Key': api_key,
        'Content-Type': 'application/json'
    }

    query_params = ''
    if len(resource_url_query_params.keys()) > 0:
        query_params = f'?{urlencode(resource_url_query_params)}'

    response = requests.get(f'{BASE_URL}{resource_url}{query_params}', headers=headers)

    if response.status_code != 200:
        raise RetrieveDataError(
            f"Não foi possível retornar os dados da frota {fleet_name} "
            f"para o recurso {resource_url}. Status: {response.status_code}"
        )

    if 'application/json' in response.headers['content-type']:
        response_dict = response.json()
        response_dict['fleet_name'] = fleet_name
        dataframe = pd.DataFrame(response_dict)
    elif 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in response.headers['content-type']:
        dataframe = pd.read_excel(response.content, worksheet_index)
        dataframe['fleet_name'] = fleet_name
    else:
        dataframe = pd.DataFrame()

    if dataframe.empty:
        return dataframe

    return flatten_nested_json_df(dataframe)


def flatten_nested_json_df(df):
    """Transforms a nested json into a one-dimensional pandas dataframe"""
    df = df.reset_index()

    # search for columns to explode/flatten
    s = (df.applymap(type) == list).all()
    list_columns = s[s].index.tolist()

    s = (df.applymap(type) == dict).all()
    dict_columns = s[s].index.tolist()

    while len(list_columns) > 0 or len(dict_columns) > 0:
        new_columns = []

        for col in dict_columns:
            # explode dictionaries horizontally, adding new columns
            horiz_exploded = pd.json_normalize(df[col]).add_prefix(f'{col}.')
            horiz_exploded.index = df.index
            df = pd.concat([df, horiz_exploded], axis=1).drop(columns=[col])
            new_columns.extend(horiz_exploded.columns)  # inplace

        for col in list_columns:
            # explode lists vertically, adding new columns
            df = df.drop(columns=[col]).join(df[col].explode().to_frame())
            new_columns.append(col)

        # check if there are still dict o list fields to flatten
        s = (df[new_columns].applymap(type) == list).all()
        list_columns = s[s].index.tolist()

        s = (df[new_columns].applymap(type) == dict).all()
        dict_columns = s[s].index.tolist()

    return df


def convert_datetime_to_unix_milliseconds(date_to_convert: datetime) -> int:
    return int(time.mktime(date_to_convert.timetuple())) * 1000


def split_intervals(start_datetime, end_datetime, days_per_interval=30):
    interval = end_datetime - start_datetime
    days = interval.days

    number_of_intervals = days // days_per_interval
    if number_of_intervals < 1:
        return [(start_datetime, end_datetime), ]

    extra_days = days % days_per_interval
    if extra_days > 0:
        number_of_intervals += 1

    intervals_list = list()
    for i in range(number_of_intervals):
        if len(intervals_list) == 0:
            interval_end = end_datetime
            interval_start = interval_end - timedelta(days=days_per_interval - 1)
        elif len(intervals_list) == number_of_intervals - 1:
            interval_end = intervals_list[-1][0] - timedelta(days=1)
            interval_start = start_datetime
        else:
            interval_end = intervals_list[-1][0] - timedelta(days=1)
            interval_start = interval_end - timedelta(days=days_per_interval - 1)

        intervals_list.append((interval_start, interval_end))

    return intervals_list
