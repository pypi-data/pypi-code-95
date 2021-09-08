"""Factory functions for SitesApi."""
import typing as tp

from bambooapi_client.model.site_data_point import SiteDataPoint
from bambooapi_client.testing.factory import faker
from bambooapi_client.testing.factory.models import (
    Factory,
    SiteDataPointFactory,
    SiteFactory,
)

import pandas as pd


def site_factory(**kwargs) -> dict:
    """Create a Site.

    Parameters
    ----------
    kwargs:
        Keyword arguments used by SiteFactory(**kwargs)

    Notes
    -----
    The return type and format matches `SitesApi:get_site`
    """
    return SiteFactory(**kwargs).to_dict()


def devices_factory(model: Factory, length: int, **kwargs) -> tp.List[dict]:
    """Create a list of model instances.

    Parameters
    ----------
    model: Factory
    length: int
        Length of the list.
    kwargs:
        Keyword arguments used by model(**kwargs)

    Notes
    -----
    The return type and format matches `SitesApi:list_devices`
    """
    return faker.list_(model, length, **kwargs)()


def forecast_factory_from_datapoints(
    datapoints: tp.List[SiteDataPoint],
) -> pd.DataFrame:
    """Create a forecast dataframe from a list of datapoints.

    Notes
    -----
    The return type and format matches `SiteApi:read_measurements` and
    `SiteApi:read_forecasts`.

    Examples
    --------
    >>> from bambooapi_client.testing.factory.models import SiteDataPointFactory
    >>> from datetime import datetime, timezone as tz
    >>> forecast_df = forecast_factory_from_datapoints([
    ...     SiteDataPointFactory(
    ...         time=datetime(2021, 5, 1, tzinfo=tz.utc),
    ...         power=15.0,
    ...         temperature=25.0,
    ...     ),
    ...     SiteDataPointFactory(
    ...         time=datetime(2021, 5, 2, tzinfo=tz.utc),
    ...         power=10.0,
    ...         temperature=20.0,
    ...      ),
    ... ])
    >>> sorted(list(forecast_df.columns))
    ['availability', 'humidity', 'mode', 'power', 'powersp', 'quality', 'schedule', 'soc', 'status', 'temperature', 'tempsp', 'vref']
    >>> forecast_df.index.name
    'time'
    >>> forecast_df['power']
    time
    2021-05-01 00:00:00+00:00    15.0
    2021-05-02 00:00:00+00:00    10.0
    Name: power, dtype: float64
    >>> forecast_df['temperature']
    time
    2021-05-01 00:00:00+00:00    25.0
    2021-05-02 00:00:00+00:00    20.0
    Name: temperature, dtype: float64
    """  # noqa: E501
    return _datapoints_list_to_dataframe(datapoints)


def forecast_factory_from_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Create a forecast dataframe from a pd.DataFrame.

    Notes
    -----
    The return type matches `SiteApi:read_measurements` and
    `SiteApi:read_forecasts`.

    Examples
    --------
    >>> import pandas as pd
    >>> from datetime import datetime, timezone as tz
    >>> df = pd.DataFrame(
    ...     [[15.0, 25.0], [10.0, 20.0]],
    ...     index=[
    ...         datetime(2021, 5, 1, tzinfo=tz.utc),
    ...         datetime(2021, 5, 2, tzinfo=tz.utc),
    ...     ],
    ...     columns=['power', 'temperature'],
    ... )
    >>> forecast_df = forecast_factory_from_dataframe(df)
    >>> sorted(list(forecast_df.columns))
    ['availability', 'humidity', 'mode', 'power', 'powersp', 'quality', 'schedule', 'soc', 'status', 'temperature', 'tempsp', 'vref']
    >>> forecast_df.index.name
    'time'
    >>> forecast_df['power']
    time
    2021-05-01 00:00:00+00:00    15.0
    2021-05-02 00:00:00+00:00    10.0
    Name: power, dtype: float64
    >>> forecast_df['temperature']
    time
    2021-05-01 00:00:00+00:00    25.0
    2021-05-02 00:00:00+00:00    20.0
    Name: temperature, dtype: float64
    """  # noqa: E501
    return _dataframe_factory(df)


def _dataframe_factory(df: pd.DataFrame) -> pd.DataFrame:
    df = df.filter(SiteDataPoint.attribute_map.keys(), axis=1)
    datapoints = [
        _datapoint_factory_from_row(index, row)
        for index, row in df.iterrows()
    ]
    return _datapoints_list_to_dataframe(datapoints)


def _datapoint_factory_from_row(
    time: pd.Timestamp,
    row: pd.Series,
) -> SiteDataPoint:
    """Transform a pd.TimeStamp and pd.Series into a DataPoint instance."""
    kwargs = {}
    kwargs.update(**row.to_dict())
    kwargs.update(
        dict(time=time.to_pydatetime())
    )
    return SiteDataPointFactory(**kwargs)


def _datapoints_list_to_dataframe(
    datapoints: tp.List[SiteDataPoint],
) -> pd.DataFrame:
    """Transform a list of SiteDataPoint instances into a pd.DataFrame."""
    return pd.DataFrame([dp.to_dict() for dp in datapoints]).set_index('time')
