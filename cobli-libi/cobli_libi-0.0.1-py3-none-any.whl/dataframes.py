from datetime import datetime

import pandas as pd

from libi.utils import get_data, convert_datetime_to_unix_milliseconds, split_intervals


PAGINATION_STEP = 50


def get_devices_data(fleet_data: dict):
    return get_data(fleet_data, 'herbie-1.1/dash/device', {})


def get_checklist_data(fleet_data: dict):
    return get_data(fleet_data, 'checklists', {})


def get_pocs_data(fleet_data: dict, start_datetime: datetime, end_datetime: datetime):
    final_dataframe = pd.DataFrame()
    for (interval_start, interval_end) in split_intervals(start_datetime, end_datetime):
        query_params = {
            'startTimestamp': convert_datetime_to_unix_milliseconds(interval_start),
            'endTimestamp': convert_datetime_to_unix_milliseconds(interval_end),
            'limit': PAGINATION_STEP,
            'offset': 0,
        }

        dataframe = pd.DataFrame()
        while True:
            _df = get_data(fleet_data, 'herbie-1.1/planning/pocs', query_params)
            if _df.empty:
                break
            elif len(_df) <= PAGINATION_STEP:
                # trying to avoid another call predicting that it will return empty results
                break

            dataframe = dataframe.append(_df)
            query_params['offset'] += PAGINATION_STEP

        final_dataframe = final_dataframe.append(dataframe)
    return final_dataframe


def get_costs_data(fleet_data: dict, start_datetime: datetime, end_datetime: datetime):
    final_dataframe = pd.DataFrame()
    for (interval_start, interval_end) in split_intervals(start_datetime, end_datetime):
        query_params = {
            'begin': convert_datetime_to_unix_milliseconds(interval_start),
            'end': convert_datetime_to_unix_milliseconds(interval_end),
            'tz': 'America/Sao_Paulo',
        }
        _df = get_data(fleet_data, 'herbie-1.1/costs/report', query_params)
        final_dataframe = final_dataframe.append(_df)
    return final_dataframe


def get_incidents_data(fleet_data: dict, start_datetime: datetime, end_datetime: datetime):
    final_dataframe = pd.DataFrame()
    for (interval_start, interval_end) in split_intervals(start_datetime, end_datetime):
        query_params = {
            'begin': convert_datetime_to_unix_milliseconds(interval_start),
            'end': convert_datetime_to_unix_milliseconds(interval_end),
            'tz': 'America/Sao_Paulo',
        }
        _df = get_data(fleet_data, 'herbie-1.1/stats/incidents/report', query_params)
        final_dataframe = final_dataframe.append(_df)
    return final_dataframe


def get_vehicle_performance_data(fleet_data: dict, start_datetime: datetime, end_datetime: datetime):
    final_dataframe = pd.DataFrame()
    for (interval_start, interval_end) in split_intervals(start_datetime, end_datetime):
        query_params = {
            'begin': convert_datetime_to_unix_milliseconds(interval_start),
            'end': convert_datetime_to_unix_milliseconds(interval_end),
            'tz': 'America/Sao_Paulo',
        }
        _df = get_data(fleet_data, 'herbie-1.1/stats/performance/vehicle/report', query_params, worksheet_index=2)
        final_dataframe = final_dataframe.append(_df)
    return final_dataframe


def get_driver_performance_data(fleet_data: dict, start_datetime: datetime, end_datetime: datetime):
    final_dataframe = pd.DataFrame()
    for (interval_start, interval_end) in split_intervals(start_datetime, end_datetime):
        query_params = {
            'begin': convert_datetime_to_unix_milliseconds(interval_start),
            'end': convert_datetime_to_unix_milliseconds(interval_end),
            'tz': 'America/Sao_Paulo',
        }
        _df = get_data(fleet_data, 'herbie-1.1/stats/performance/driver/report', query_params, worksheet_index=2)
        final_dataframe = final_dataframe.append(_df)
    return final_dataframe
