import datetime
import bs4
import requests


def ObtainWikiSNP500Symbols():
    """
    Download and parse the Wikipdeia list of S&P500 constituents using
    requests and BeautifulSoup.

    Returns a list of tuples for to add to MySQL.
    """
    # Stores the current time, for the created_date and last_updated_date
    timestamp = datetime.datetime.utcnow()

    # Use requests and BeautifulSoup to download the
    # list of S&P500 companies and obtain the symbol table
    response = requests.get("http://en.wikipedia.org/wiki/List_of_S%26P_500_companies")

    # Parse the response using html.parser
    soup = bs4.BeautifulSoup(response.text, features="html.parser")

    # This selects the first table, using CSS Selector syntax
    # and then ignores the header row ([1:])
    raw_symbol_list = soup.select("table")[0].select("tr")[1:]

    # Stores the records needed for the symbol table
    rows = []

    for i, symbol in enumerate(raw_symbol_list):
        tds = symbol.select("td")
        rows.append(
            (
                tds[0].select("a")[0].text,
                "stock",
                tds[1].select("a")[0].text,
                tds[3].text,
                "USD",
                timestamp,
                timestamp,
            )
        )

    print("Downloaded %s symbols." % len(rows))

    return rows
