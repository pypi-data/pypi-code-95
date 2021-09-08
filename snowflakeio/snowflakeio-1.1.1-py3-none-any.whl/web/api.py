import numpy as np  # The Numpy numerical computing library
import pandas as pd  # The Pandas data science library
import requests  # The requests library for HTTP requests in Python
from bs4 import BeautifulSoup


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
