""" All api's related to current spot market activity """

from bitxchange.api import API
from bitxchange.errors import TargetPairError


class Market(API):
    def available_trading_pairs(self):
        """
        Description: Returns a list of all active trading pairs currently
        support by the exchange

        GET /api/available_pairs

        Args: None

        KWargs: None
        """

        url_path = "/api/available_pairs"
        return self.query_exchange(url_path)

    def all_market_tickers(self):
        """
        Description: Returns current spot tickers for all active pairs on
        the exchange

        GET /api/tickers

        Args: None

        KWargs: None
        """

        url_path = "/api/tickers"
        return self.query_exchange(url_path)

    def volume_24h(self):
        """
        Description: Returns the current 24 hour trade volume of each active
        trade pair available on the exchange.

        GET /api/volume24

        Args: None

        KWargs: None
        """

        url_path = "/api/volume24"
        return self.query_exchange(url_path)

    def specific_market_ticker(self, target_pair):
        """
        Description: Returns the latest ticker for the target pair provided.

        GET /api/ticker/<target_pair>

        Args:
            - target_pair <str>

        KWargs: None
        """

        url_path = f"/api/ticker/{target_pair}"
        target = self.query_exchange(url_path)

        if target["status"] == 1:
            return target

        raise TargetPairError(target_pair)

    def order_book(self, target_pair):
        """
        Description: Returns current orderbook for the target pair.

        GET /api/order_book/<target_pair>

        Args:
            - target_pair <str>

        KWargs: None
        """

        url_path = f"/api/order_book/{target_pair}"
        target = self.query_exchange(url_path)

        if target["status"] == 1:
            return target

        raise TargetPairError(target_pair)

    def trade_history(self, target_pair):
        """
        Description: displays the trade history of the target pair

        GET /api/trade_history/<target_pair>

        Args:
            - target_pair <str>

        KWargs: None
        """

        url_path = f"/api/trade_history/{target_pair}"
        target = self.query_exchange(url_path)

        if target["status"] == 1:
            return target

        raise TargetPairError(target_pair)
