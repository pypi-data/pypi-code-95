from __future__ import absolute_import, annotations
from typing import Any, Dict, Optional, Union
from urllib.parse import urlencode

import pandas as pd
import requests

from .api_config import ApiConfig
from . import common


def get_daily_snapshot(
        output_format: Optional[str] = None,
        api_key: Optional[str] = None) -> Union[pd.DataFrame, str, Dict[str, Any]]:
    """
    Get latest point-in-time snapshot of our data-driven predictions for all issuers along
    with associated metadata.

    Args:
        output_format:                  One-of 'pandas', 'json', or 'csv'.
        api_key:                        Your Migrations.ML API key.

    Returns:
        Union[DataFrame, str, Dict[str, Any]]


    """

    api_key = common.get_api_key(api_key)
    output_format = common.get_output_format(output_format)

    query_params = {
        'api_key': api_key
    }
    url = ApiConfig.endpoint_base + '/dailySnapshot?' + urlencode(query_params)

    try:

        response = requests.get(url)

    except Exception as error:
        raise ConnectionError(
            'Failed to make request to Migrations.ML API: %s', error) from error

    if not response.ok:

        raise RuntimeError(
            'Migrations.ML API returned bad response: %s', response.reason)

    reponse_body = response.json()

    if reponse_body['status'] != 'success':

        raise RuntimeError('Migrations.ML API returned bad status')

    if output_format == 'json':

        return reponse_body

    dataframe = pd.DataFrame([
        {
            **{k: v for k, v in row.items() if k not in 'transparency_factors'},
            'transparency_equity_performance': row['transparency_factors']['equity_performance'],
            'transparency_leverage': row['transparency_factors']['leverage'],
            'transparency_macro': row['transparency_factors']['macro'],
            'transparency_market_value': row['transparency_factors']['market_value'],
            'transparency_profitability': row['transparency_factors']['profitability'],
            'transparency_solvency': row['transparency_factors']['solvency'],
        }
        for row in reponse_body['results']
    ])

    if output_format == 'csv':

        return dataframe.to_csv(index=False)

    assert output_format == 'pandas'

    return dataframe
