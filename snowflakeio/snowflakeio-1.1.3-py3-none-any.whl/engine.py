from snowflakeio.tokens import IEX_CLOUD_API_TOKEN


class Profile:
    def __init__(self, symbol):
        self.symbol = symbol


def initialize(symbol: str = None) -> Profile:
    return Profile(symbol or "AAPL")
