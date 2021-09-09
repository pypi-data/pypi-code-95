from __future__ import absolute_import, annotations
import datetime as dt

import numpy as np

from .api_config import ApiConfig


def get_api_key(api_key: str) -> str:

    if api_key is None:

        if (api_key := ApiConfig.api_key) is None:

            raise ValueError(
                'API key must be set either gloally or passed as an argument.')

    return api_key


def get_output_format(output_format: str) -> str:

    if output_format is None:

        output_format = ApiConfig.output_format

    if output_format not in {'pandas', 'json', 'csv'}:

        raise ValueError(
            'output_format must be one-of pandas, json, or csv.')

    return output_format


def validate_identifier(identifier: str, identifier_type: str):

    if not isinstance(identifier, str) or len(identifier) == 0:
        raise ValueError('Argument identifier must be non-empty str')

    if identifier_type not in {'ticker', 'lei'}:
        raise ValueError(
            'Argument identifier_type must be one-of ticker or lei')


def parse_tenor_points(tenor_points):

    if tenor_points is None:
        return None

    if isinstance(tenor_points, np.ndarray):
        if len(tenor_points.shape) != 1:
            raise ValueError(
                'When tenor_points is expressed as numpy array, dimension must be 1')
        tenor_points = tenor_points.tolist()

    if not isinstance(tenor_points, (list, tuple)):
        tenor_points = [tenor_points, ]

    if len(tenor_points) > 20:
        raise ValueError(
            'A maximum of 20 tenor points are allowed per request')

    if not all(isinstance(point, (float, int)) for point in tenor_points):
        raise ValueError(
            'All elements of argument tenor_points must be float or int')

    if any(x < 1. or x > 40. for x in tenor_points):
        raise ValueError(
            'All tenor points must be in interval [1, 40]')

    return tenor_points


def validate_dates(start_date, end_date):

    def _validate_date(date_):

        if date_ is None:
            return date_, date_

        if isinstance(date_, (dt.date, dt.datetime)):
            if isinstance(date_, dt.datetime):
                date_ = date_.date()

            return date_.strftime('%Y-%m-%d'), date_

        if isinstance(date_, str):

            try:
                date_parsed = dt.datetime.strptime(date_, '%Y-%m-%d').date()

            except ValueError as error:
                raise ValueError('date must be format %Y-%m-%d: %s', error)

            return date_, date_parsed

    start_date, start_date_parsed = _validate_date(start_date)
    end_date, end_date_parsed = _validate_date(end_date)

    if start_date is not None and end_date is not None:

        if start_date_parsed > end_date_parsed:
            raise ValueError('start_date must be <= end_date')

    return start_date, end_date
