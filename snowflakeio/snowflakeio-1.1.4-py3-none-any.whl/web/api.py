import math

import numpy as np  # The Numpy numerical computing library
import pandas as pd  # The Pandas data science library
import requests  # The requests library for HTTP requests in Python
from bs4 import BeautifulSoup

from snowflakeio.engine import Profile
from snowflakeio.tokens import IEX_CLOUD_API_TOKEN


def current_snp500_list(symbols_only: bool = False) -> np.ndarray:
    """Downloads the current companies listed on the S&P 500 market

    Returns:
    -----------
    numpy.darray
        [id, company name, company symbol]
    """
    page = requests.get("https://www.slickcharts.com/sp500", headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(page.text, "html.parser")
    table = soup.find("table", class_="table table-hover table-borderless table-sm")
    df = pd.read_html(str(table))[0]
    if symbols_only:
        return np.asarray(df[["#", "Company", "Symbol"]].to_numpy()[:, 2])
    else:
        return df[["#", "Company", "Symbol"]].to_numpy()


def quote(profile: Profile):
    url = f"https://sandbox.iexapis.com/stable/stock/{profile.symbol}/quote?token={IEX_CLOUD_API_TOKEN}"
    data = requests.get(url).json()
    return np.asarray([profile.symbol, data["latestPrice"], data["marketCap"]])


def __x(arr, n):
    for i in range(0, len(arr), n):
        yield arr[i : i + n]


def batch_quotes(symbols: np.ndarray, order_of: int):
    """Generates a numpy array of S&P500 stocks

    Args:
    -----------
    symbols: The list of symbols to find market information for.

    order_of: The set of batches to group the symbol in to satisfy the api request. (max: 100)

    Returns:
    -----------
    numpy.ndarray
        [[symbol, lastest_price, market_capitalization]]
    """
    # Group the array of symbols into a 2d array of symbols x order_of using a generator
    x = list(__x(symbols, order_of))
    y = []
    # Stores the 2d array -> [[symbol, latest_price, market_cap]]
    f = []
    # Convert each group of symbols into a stringified versioned group
    # -> [[AAPL, MSFT]] becomes [['AAPL,MSFT']]
    for i in range(0, len(x)):
        y.append(",".join(x[i]))
    # For each string group
    for g in y:
        # Fetch the batch response for the current symbols group
        url = f"https://sandbox.iexapis.com/stable/stock/market/batch/?types=quote&symbols={g}&token={IEX_CLOUD_API_TOKEN}"
        res = requests.get(url).json()
        # For each symbol in the current iteration's group
        for s in g.split(","):
            # [symbol, latest_price, market_cap]
            f.append([s, float(res[s]["quote"]["latestPrice"]), float(res[s]["quote"]["marketCap"])])
    # Return the 2d array -> [[symbol, latest_price, market_cap]] as a np array
    return np.asarray(f)
