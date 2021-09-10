from __future__ import absolute_import, annotations
from typing import Any, Dict, Optional, Union, List
from urllib.parse import urlencode
from pprint import pprint
import datetime as dt

import pandas as pd
import numpy as np
import requests

from .api_config import ApiConfig
from . import common


def get_yield_curve(
        identifier: str,
        identifier_type: str = 'ticker',
        tenor_points: Optional[Union[float, List[float]]] = None,
        output_format: Optional[str] = None,
        api_key: Optional[str] = None) -> Union[pd.DataFrame, str, Dict[str, Any]]:
    """
    Get latest point-in-time snapshot of our data-driven predictions for all issuers along
    with associated metadata.

    Args:
        identifier:                     Identifier of issuer.
        identifier_type:                One-of 'ticker' or 'lei'.
        tenor_points:                   Value or list of values of time-to-maturity in years.
        output_format:                  One-of 'pandas', 'json', or 'csv'.
        api_key:                        Your Migrations.ML API key.

    Returns:
        Union[DataFrame, str, Dict[str, Any]]


    """

    api_key = common.get_api_key(api_key)
    output_format = common.get_output_format(output_format)
    common.validate_identifier(identifier, identifier_type)
    tenor_points = common.parse_tenor_points(tenor_points)

    query_params = {
        'api_key': api_key,
        'identifier': identifier,
        'identifier_type': identifier_type,
    }
    if tenor_points is not None:
        # pass
        query_params['tenor_points'] = ','.join(
            str(point) for point in tenor_points)
    url = ApiConfig.endpoint_base + '/yieldCurve?' + urlencode(query_params)

    try:

        response = requests.get(url)

    except Exception as error:
        raise ConnectionError(
            'Failed to make request to Migrations.ML API: %s', error) from error

    if not response.ok:

        raise RuntimeError(
            'Migrations.ML API returned bad response: %s', response.reason)

    response_body = response.json()

    if not response_body['success']:

        raise RuntimeError('Migrations.ML API returned bad status')

    if output_format == 'json':

        return response_body

    dataframe = pd.DataFrame([
        {
            **{k: v for k, v in response_body.items() if k not in {'tenor_points', 'success', 'reason'}},
            **point
        }
        for point in response_body['tenor_points']
    ])

    if output_format == 'csv':

        return dataframe.to_csv(index=False)

    assert output_format == 'pandas'

    return dataframe


def get_yield_curve_history(
        identifier: str,
        identifier_type: str = 'ticker',
        tenor_points: Optional[Union[float, List[float]]] = None,
        start_date: Union[dt.date, str] = None,
        end_date: Union[dt.date, str] = None,
        output_format: Optional[str] = None,
        api_key: Optional[str] = None) -> Union[pd.DataFrame, str, Dict[str, Any]]:
    """
    Get latest point-in-time snapshot of our data-driven predictions for all issuers along
    with associated metadata.

    Args:
        identifier:                     Identifier of issuer.
        identifier_type:                One-of 'ticker' or 'lei'.
        tenor_points:                   Value or list of values of time-to-maturity in years.
        start_date:                     Left endpoint of date interval.
        end_date:                       Right endpoint of date interval.
        output_format:                  One-of 'pandas', 'json', or 'csv'.
        api_key:                        Your Migrations.ML API key.

    Returns:
        Union[DataFrame, str, Dict[str, Any]]


    """

    api_key = common.get_api_key(api_key)
    output_format = common.get_output_format(output_format)
    common.validate_identifier(identifier, identifier_type)
    tenor_points = common.parse_tenor_points(tenor_points)
    start_date, end_date = common.validate_dates(start_date, end_date)

    query_params = {
        'api_key': api_key,
        'identifier': identifier,
        'identifier_type': identifier_type,
    }

    if tenor_points is not None:
        query_params['tenor_points'] = ','.join(
            str(point) for point in tenor_points)

    if start_date is not None:
        query_params['start_date'] = start_date

    if end_date is not None:
        query_params['end_date'] = end_date

    url = ApiConfig.endpoint_base + \
        '/yieldCurveHistory?' + urlencode(query_params)

    try:

        response = requests.get(url)

    except Exception as error:
        raise ConnectionError(
            'Failed to make request to Migrations.ML API: %s', error) from error

    if not response.ok:

        raise RuntimeError(
            'Migrations.ML API returned bad response: %s', response.reason)

    response_body = response.json()

    if not response_body['success']:

        error_msg = 'Migrations.ML API bad status: %s' % response_body['reason']
        raise RuntimeError(error_msg)

    if output_format == 'json':

        return response_body

    meta = {
        k: v
        for k, v in response_body.items()
        if k not in {'timeseries', 'success', 'reason'}
    }

    data = [
        {
            'date': record['date'],
            **meta,
            **point
        }
        for record in response_body['timeseries']
        for point in record['tenor_points']
    ]

    dataframe = pd.DataFrame(data)

    if output_format == 'csv':

        return dataframe.to_csv(index=False)

    assert output_format == 'pandas'

    return dataframe
