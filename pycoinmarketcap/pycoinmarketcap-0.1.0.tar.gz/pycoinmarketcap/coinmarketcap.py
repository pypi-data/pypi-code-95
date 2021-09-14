from __future__ import annotations

from typing import Dict, List
from requests import Session, models
from .response import Response
from .errors import *


API_DOMAIN = "https://pro-api.coinmarketcap.com/v1"
SANDBOX_API = "https://sandbox-api.coinmarketcap.com/v1"
SANDBOX_API_KEY = "b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c"


class CoinMarketCap:
    """CoinMarketCap API Wrapper

    Documentation: https://coinmarketcap.com/api/documentation/v1/
    """

    def __init__(self, api_key: str) -> None:
        """
        Args:
            api_key (str): Your CoinMarketCap API_KEY
        """
        self.api_key = api_key
        self.__session = Session()
        self.__headers = {"Accept": "application/json", "X-CMC_PRO_API_KEY": api_key}

    def __cleanNoneItems(self, d: Dict):
        # https://betterprogramming.pub/how-to-remove-null-none-values-from-a-dictionary-in-python-1bedf1aab5e4
        return {k: v for k, v in d.items() if v is not None}

    def __get(self, url: str, **params) -> Dict:
        """Internal function url request getter

        Args:
            url (str): url to request
            params (Dict): url parameters

        Returns:
            [type]: Dict
        """

        r: models.Response = self.__session.get(
            API_DOMAIN + url,
            params=self.__cleanNoneItems(params),
            headers=self.__headers,
        )
        data = r.json()

        if r.status_code != 200:
            self.__raise_error(r.status_code, data["status"])

        return data

    def __raise_error(self, code: int, status: Dict) -> None:
        """Function of raising errors depending on status code.

        Args:
            code (int): the status code
            status (Dict): the response status object

        Raises:
            ErrorUnauthorized: 401 Unauthorized
            ErrorForbidden: 403 Forbidden
            ErrorTooManyRequests: 429 Too Many Requests
            ErrorInternalServerError: 500 Internal Server Error
            ErrorBadRequest: 400 Bad Request
        """

        if code == 401:
            raise ErrorUnauthorized(status)
        elif code == 403:
            raise ErrorForbidden(status)
        elif code == 429:
            raise ErrorTooManyRequests(status)
        elif code == 500:
            raise ErrorInternalServerError(status)

        raise ErrorBadRequest(status)

    def crypto_airdrop(self, id: str) -> Response[Dict]:
        """Returns information about a single airdrop available on CoinMarketCap.
        Includes the cryptocurrency data.

        Args:
            id (str): Airdrop Unique ID. This can be found using the Aidrops API.
        """
        return Response[Dict](self.__get(f"/cryptocurrency/airdrop", id=id))

    def crypto_airdrops(
        self,
        start: int = 1,
        limit: int = None,
        status: str = "ONGOING",
        id: str = None,
        slug: str = None,
        symbol: str = None,
    ) -> Response[List]:
        """Returns a list of past, present, or future airdrops which have run on CoinMarketCap.

        Args:
            start (int, optional): Page to return the result. Defaults to 1.
            limit (int, optional): Limit the number of result. Defaults to None.
            status (str): Status of airdrops.
                    Valid Values: ["ENDED", "ONGOING", "UPCOMING"] (default: "ONGOING")
            id (str, optional): Filter by one cryptocurrency CoinMarketCap ID.
                    Example: 1 . Defaults to None.
            slug (str, optional): Filter by list of cryptocurrency slugs.
                    Example: "bitcoin,ethereum" . Defaults to None.
            symbol (str, optional): Filter by cryptocurrency symbols.
                    Example: "BTC,ETH" . Defaults to None.
        """
        return Response[List](
            self.__get(
                f"/cryptocurrency/airdrops",
                start=start,
                limit=limit,
                status=status,
                id=id,
                slug=slug,
                symbol=symbol,
            )
        )

    def crypto_categories(
        self,
        start: int = 1,
        limit: int = None,
        id: str = None,
        slug: str = None,
        symbol: str = None,
    ) -> Response[List[Dict]]:
        """Returns information about all coin categories available on CoinMarketCap. Includes a
        paginated list of cryptocurrency quotes and metadata from each category.

        Args:
            start (int, optional): Page to return the result. Defaults to 1.
            limit (int, optional): Limit the number of result. Defaults to None.
            id (str, optional): Filter by cryptocurrency CoinMarketCap IDs.
                    Example: 1,2 . Defaults to None.
            slug (str, optional): Filter by list of cryptocurrency slugs.
                    Example: "bitcoin,ethereum" . Defaults to None.
            symbol (str, optional): Filter by cryptocurrency symbols.
                    Example: "BTC,ETH" . Defaults to None.

        Returns:
            [type]: [description]
        """

        return Response[List[Dict]](
            self.__get(
                f"/cryptocurrency/categories",
                start=start,
                limit=limit,
                id=id,
                slug=slug,
                symbol=symbol,
            )
        )

    def crypto_category(
        self,
        id: str,
        start: int = 1,
        limit: int = 100,
        convert: str = None,
        convert_id: str = None,
    ) -> Response[Dict]:
        """Returns information about a single coin category available on CoinMarketCap. Includes
        a paginated list of the cryptocurrency quotes and metadata for the category.

        Args:
            id (str): The Category ID. This can be found using the Categories API.
            start (int, optional): Page to return the result. Defaults to 1.
            limit (int, optional): Limit the number of results. Defaults to 100.
            convert (str, optional): Calculate each market quote in up to 120 currency symbols.
                    Example: "USD,ALL". Defaults to None.
            convert_id (str, optional): Calculate each market quote using CoinMarketCap IDs instead of symbol.
                    Can't be used with convert. Example: "1,2781". Defaults to None.

        Returns:
            [type]: [description]
        """

        return Response[Dict](
            self.__get(
                f"/cryptocurrency/category",
                id=id,
                start=start,
                limit=limit,
                convert=convert,
                convert_id=convert_id,
            )
        )

    def crypto_metadata(
        self,
        id: str = None,
        slug: str = None,
        symbol: str = None,
        address: str = None,
        aux: str = "urls,logo,description,tags,platform,date_added,notice",
    ) -> Response[Dict]:
        """Returns all static metadata available for one or more cryptocurrencies.
         This information includes details like logo, description, official website URL,
         social links, and links to a cryptocurrency's technical documentation.

        Args:
            id (str, optional): One or more comma-separated CoinMarketCap cryptocurrency IDs.
                    Example: "1,2". Defaults to None.
            slug (str, optional): Comma-separated cryptocurrency slugs. Example: "bitcoin,ethereum".
                    Defaults to None.
            symbol (str, optional): Comma-separated cryptocurrency symbols. Example: "BTC,ETH".
                    Defaults to None.
            address (str, optional): Contract Adddress of the cryptocurrency. Defaults to None.
            aux (str, optional): Comma-separated list of supplemental data fields to return.
                    Defaults to "urls,logo,description,tags,platform,date_added,notice".

        Returns:
            [type]: [description]
        """
        return Response[Dict](
            self.__get(
                "/cryptocurrency/info",
                id=id,
                slug=slug,
                symbol=symbol,
                address=address,
                aux=aux,
            )
        )

    def crypto_map(
        self,
        listing_status: str = "active",
        start: int = 1,
        limit: int = None,
        sort: str = "id",
        symbol: str = None,
        aux: str = "platform,first_historical_data,last_historical_data,is_active",
    ) -> Response[List[Dict]]:
        """Returns a mapping of all cryptocurrencies to unique CoinMarketCap ids.

        Args:
            listing_status (str, optional): Listing status of cryptocurrencies.
                    Valid Values: "inactive,untracked,active". Defaults to "active".
            start (int, optional): Page to return the result. Defaults to 1.
            limit (int, optional): Limit the number of result. Defaults to None.
            sort (str, optional): Sort the list of cryptocurrencies.
                    Valid Valus: "cmc_rank" "id". Defaults to "id".
            symbol (str, optional): Filter by cryptocurrency symbols.
                    Example: "BTC,ETH" . Defaults to None.
            aux (str, optional): Comma-separated list of supplemental data fields to return.
                    Defaults to "platform,first_historical_data,last_historical_data,is_active".

        Returns:
            [type]: [description]
        """
        return Response[List[Dict]](
            self.__get(
                "/cryptocurrency/map",
                listing_status=listing_status,
                start=start,
                limit=limit,
                sort=sort,
                symbol=symbol,
                aux=aux,
            )
        )

    def crypto_listings_historical(
        self,
        date: str,
        start: int = 1,
        limit: int = 100,
        convert: str = None,
        convert_id: str = None,
        sort: str = "cmc_rank",
        sort_dir: str = "asc",
        cryptocurrency_type: str = "all",
        aux: str = "platform,tags,date_added,circulating_supply,total_supply,max_supply,cmc_rank,num_market_pairs",
    ) -> Response[List[Dict]]:
        """Returns a ranked and sorted list of all cryptocurrencies for a historical UTC date.

        Args:
            date (str): date (Unix or ISO 8601) to reference day of snapshot.
            start (int, optional): Page to return the result. Defaults to 1.
            limit (int, optional): Limit the number of result. Defaults to 100.
            convert (str, optional): Calculate each market quote in up to 120 currency symbols.
                    Example: "USD,ALL". Defaults to None.
            convert_id (str, optional): Calculate each market quote using CoinMarketCap IDs instead of symbol.
                    Can't be used with convert. Example: "1,2781". Defaults to None.
            sort (str, optional): Sort the list of cryptocurrencies.
                    Valid Valus: "cmc_rank" "name" "symbol" "market_cap" "price" "circulating_supply"
                    "total_supply" "max_supply" "num_market_pairs" "volume_24h" "percent_change_1h"
                    "percent_change_24h" "percent_change_7d". Defaults to "id".
            sort_dir (str, optional): Sort the order against the date.
                    Valid Values: "asc" "desc". Defaults to "asc".
            cryptocurrency_type (str, optional): The type of cryptocurrency to include.
                    Valid Values: "all" "coins" "tokens". Defaults to "all".
            aux (str, optional): Comma-separated list of supplemental data fields to return.
                    Defaults to "platform,tags,date_added,circulating_supply,total_supply,max_supply,cmc_rank,num_market_pairs".

        Returns:
            [type]: [description]
        """
        return Response[List[Dict]](
            self.__get(
                "/cryptocurrency/listings/historical",
                date=date,
                start=start,
                limit=limit,
                convert=convert,
                convert_id=convert_id,
                sort=sort,
                sort_dir=sort_dir,
                cryptocurrency_type=cryptocurrency_type,
                aux=aux,
            )
        )

    def crypto_listings_latest(
        self,
        start: int = 1,
        limit: int = 100,
        price_min: float = None,
        price_max: float = None,
        market_cap_min: float = None,
        volume_24h_min: float = None,
        volume_24h_max: float = None,
        circulating_supply_min: float = None,
        circulating_supply_max: float = None,
        percent_change_24h_min: float = None,
        percent_change_24h_max: float = None,
        convert: str = None,
        convert_id: str = None,
        sort: str = "market_cap",
        sort_dir: str = None,
        cryptocurrency_type: str = "all",
        tag: str = "all",
        aux: str = "num_market_pairs,cmc_rank,date_added,tags,platform,max_supply,circulating_supply,total_supply",
    ) -> Response[List[Dict]]:
        """Returns a paginated list of all active cryptocurrencies with latest market data.

        Args:
            start (int, optional): Page to return the result. Defaults to 1.
            limit (int, optional): Limit the number of result. Defaults to 100.
            price_min (float, optional): Optionally specify a threshold of minimum USD price to filter results by.
                    Defaults to None.
            price_max (float, optional): Optionally specify a threshold of maximum USD price to filter results by.
                    Defaults to None.
            market_cap_min (float, optional): Optionally specify a threshold of minimum market cap to filter results by.
                    Defaults to None.
            volume_24h_min (float, optional): Optionally specify a threshold of minimum 24 hour USD volume to filter results by.
                    Defaults to None.
            volume_24h_max (float, optional): Optionally specify a threshold of maximum 24 hour USD volume to filter results by.
                    Defaults to None.
            circulating_supply_min (float, optional): Optionally specify a threshold of minimum circulating supply to filter results by.
                    Defaults to None.
            circulating_supply_max (float, optional): Optionally specify a threshold of maximum circulating supply to filter results by.
                    Defaults to None.
            percent_change_24h_min (float, optional): Optionally specify a threshold of minimum 24 hour percent change to filter results by.
                    Defaults to None.
            percent_change_24h_max (float, optional): Optionally specify a threshold of maximum 24 hour percent change to filter results by.
                    Defaults to None.
            convert (str, optional): Calculate each market quote in up to 120 currency symbols.
                    Example: "USD,ALL". Defaults to None.
            convert_id (str, optional): Calculate each market quote using CoinMarketCap IDs instead of symbol.
                    Can't be used with convert. Example: "1,2781". Defaults to None.
            sort (str, optional): Sort the list of cryptocurrencies. Valid Values: "name" "symbol" "date_added" "market_cap"
                    "market_cap_strict" "price" "circulating_supply" "total_supply" "max_supply" "num_market_pairs" "volume_24h"
                    "percent_change_1h" "percent_change_24h" "percent_change_7d" "market_cap_by_total_supply_strict" "volume_7d" "volume_30d".
                    Defaults to "market_cap".
            sort_dir (str, optional): Sort the order against the specified sort.
                    Defaults to None.
            cryptocurrency_type (str, optional): The type of cryptocurrency to include.
                    Valid Values: "all" "coins" "tokens". Defaults to "all".
            tag (str, optional): The tag of cryptocurrency to include. Valid Values: "all" "defi" "filesharing".
                    Defaults to "all".
            aux (str, optional): Comma-separated list of supplemental data fields to return.
                    Defaults to "num_market_pairs,cmc_rank,date_added,tags,platform,max_supply,circulating_supply,total_supply".

        Returns:
            [type]: [description]
        """
        return Response[List[Dict]](
            self.__get(
                "/cryptocurrency/listings/latest",
                start=start,
                limit=limit,
                price_min=price_min,
                price_max=price_max,
                market_cap_min=market_cap_min,
                volume_24h_min=volume_24h_min,
                volume_24h_max=volume_24h_max,
                circulating_supply_min=circulating_supply_min,
                circulating_supply_max=circulating_supply_max,
                percent_change_24h_min=percent_change_24h_min,
                percent_change_24h_max=percent_change_24h_max,
                convert=convert,
                convert_id=convert_id,
                sort=sort,
                sort_dir=sort_dir,
                cryptocurrency_type=cryptocurrency_type,
                tag=tag,
                aux=aux,
            )
        )

    def crypto_marketpairs_latest(
        self,
        id: str = None,
        slug: str = None,
        symbol: str = None,
        start: int = 1,
        limit: int = 100,
        sort_dir: str = "desc",
        sort: str = "volume_24h_strict",
        aux: str = "num_market_pairs,category,fee_type",
        matched_id: str = None,
        matched_symbol: str = None,
        category: str = "all",
        fee_type: str = "all",
        convert: str = None,
        convert_id: str = None,
    ) -> Response[Dict]:
        """Lists all active market pairs that CoinMarketCap tracks for a given cryptocurrency or fiat currency.

        Args:
            id (str, optional): A cryptocurrency or fiat currency by CoinMarketCap ID to list market pairs for.
                    Example: "1". Defaults to None.
            slug (str, optional): Alternatively pass a cryptocurrency by slug.
                    Example: "bitcoin". Defaults to None.
            symbol (str, optional): Alternatively pass a cryptocurrency by symbol. Fiat currencies are not supported
                    by this field. Example: "BTC". Defaults to None.
            start (int, optional): Page to return the result. Defaults to 1.
            limit (int, optional): Limit the number of result. Defaults to 100.
            sort_dir (str, optional): Sort direction of markets returned. Defaults to "desc".
            sort (str, optional): Sort the order of markets returned. Valid Values: "volume_24h_strict" "cmc_rank"
                    "cmc_rank_advanced" "effective_liquidity" "market_score" "market_reputation". Defaults to "volume_24h_strict".
            aux (str, optional): Comma-separated list of supplemental data fields to return.
                    Defaults to "num_market_pairs,category,fee_type".
            matched_id (str, optional): Include one or more fiat or cryptocurrency IDs to filter market pairs by.
                    Parameter cannot be used with matched_symbol. Defaults to None.
            matched_symbol (str, optional): Include one or more fiat or cryptocurrency symbols to filter market pairs by.
                    Parameter cannot be used with matched_symbol. Defaults to None.
            category (str, optional): The category of trading the market falls under.
                    Valid Values: "all" "spot" "derivatives" "otc" "perpetual". Defaults to "all".
            fee_type (str, optional): The fee type the exchange enforces for this market.
                    Valid Values: "all" "percentage" "no-fees" "transactional-mining" "unknown". Defaults to "all".
            convert (str, optional): Calculate each market quote in up to 120 currency symbols.
                    Example: "USD,ALL". Defaults to None.
            convert_id (str, optional): Calculate each market quote using CoinMarketCap IDs instead of symbol.
                    Can't be used with convert. Example: "1,2781". Defaults to None.

        Returns:
            [type]: [description]
        """
        return Response[Dict](
            self.__get(
                "/cryptocurrency/market-pairs/latest",
                id=id,
                slug=slug,
                symbol=symbol,
                start=start,
                limit=limit,
                sort_dir=sort_dir,
                sort=sort,
                aux=aux,
                matched_id=matched_id,
                matched_symbol=matched_symbol,
                category=category,
                fee_type=fee_type,
                convert=convert,
                convert_id=convert_id,
            )
        )

    def crypto_ohlcv_historical(
        self,
        id: str = None,
        slug: str = None,
        symbol: str = None,
        time_period: str = "daily",
        time_start: str = None,
        time_end: str = None,
        count: int = 10,
        interval: str = "daily",
        convert: str = None,
        convert_id: str = None,
        skip_invalid: bool = False,
    ) -> Response[Dict]:
        """Returns historical OHLCV (Open, High, Low, Close, Volume) data along with
        market cap for any cryptocurrency using time interval parameters. At least
        one "id" or "slug" or "symbol" is required for this request.

        Args:
            id (str, optional): One or more comma-separated CoinMarketCap cryptocurrency IDs. Example: "1,1027". Defaults to None.
            slug (str, optional): Alternatively pass a comma-separated list of cryptocurrency slugs. Example: "bitcoin,ethereum". Defaults to None.
            symbol (str, optional): Alternatively pass one or more comma-separated cryptocurrency symbols. Example: "BTC,ETH". Defaults to None.
            time_period (str, optional): Time period to return OHLCV data for. Defaults to "daily".
            time_start (str, optional): Timestamp (Unix or ISO 8601) to start returning OHLCV time periods for.
                    Defaults to None.
            time_end (str, optional): Timestamp (Unix or ISO 8601) to stop returning OHLCV time periods for (inclusive).
                    Defaults to None.
            count (int, optional): Limit the number of results. Defaults to 10.
            interval (str, optional): [description]. Valid Values: "hourly" "daily" "weekly" "monthly" "yearly" "1h" "2h" "3h" "4h" "6h" "12h"
                    "1d" "2d" "3d" "7d" "14d" "15d" "30d" "60d" "90d" "365d".
                    Defaults to "daily".
            convert (str, optional): Calculate each market quote in up to 120 currency symbols.
                    Example: "USD,ALL". Defaults to None.
            convert_id (str, optional): Calculate each market quote using CoinMarketCap IDs instead of symbol.
                    Can't be used with convert. Example: "1,2781". Defaults to None.
            skip_invalid (bool, optional): Skip invalid lookups / result. Defaults to False.

        Returns:
            [type]: [description]
        """
        return Response[Dict](
            self.__get(
                "/cryptocurrency/ohlcv/historical",
                id=id,
                slug=slug,
                symbol=symbol,
                time_period=time_period,
                time_start=time_start,
                time_end=time_end,
                count=count,
                interval=interval,
                convert=convert,
                convert_id=convert_id,
                skip_invalid=skip_invalid,
            )
        )

    def crypto_ohlcv_latest(
        self,
        id: str = None,
        symbol: str = None,
        convert: str = None,
        convert_id: str = None,
        skip_invalid: bool = False,
    ) -> Response[Dict]:
        """Returns the latest OHLCV (Open, High, Low, Close, Volume) market values for one or more cryptocurrencies for the current UTC day.

        Args:
            id (str, optional): One or more comma-separated cryptocurrency CoinMarketCap IDs. Example: 1,2.
                    Defaults to None.
            symbol (str, optional): Alternatively pass one or more comma-separated cryptocurrency symbols. Example: "BTC,ETH".
                    Defaults to None.
            convert (str, optional): Calculate each market quote in up to 120 currency symbols.
                    Example: "USD,ALL". Defaults to None.
            convert_id (str, optional): Calculate each market quote using CoinMarketCap IDs instead of symbol.
                    Can't be used with convert. Example: "1,2781". Defaults to None.
            skip_invalid (bool, optional): Skip invalid lookups / result. Defaults to False.

        Returns:
            [type]: [description]
        """
        return Response[Dict](
            self.__get(
                "/cryptocurrency/ohlvc/latest",
                id=id,
                symbol=symbol,
                convert=convert,
                convert_id=convert_id,
                skip_invalid=skip_invalid,
            )
        )

    def crypto_price_performance_stats_latest(
        self,
        id: str = None,
        slug: str = None,
        symbol: str = None,
        time_period: str = "all_time",
        convert: str = None,
        convert_id: str = None,
        skip_invalid: bool = False,
    ) -> Response[Dict]:
        """Returns price performance statistics for one or more cryptocurrencies including launch price ROI and all-time high / all-time low.

        Args:
            id (str, optional): One or more comma-separated cryptocurrency CoinMarketCap IDs. Example: 1,2.
                    Defaults to None.
            slug (str, optional): Alternatively pass a comma-separated list of cryptocurrency slugs.
                    Example: "bitcoin,ethereum". Defaults to None.
            symbol (str, optional): Alternatively pass one or more comma-separated cryptocurrency symbols.
                    Example: "BTC,ETH". Defaults to None.
            time_period (str, optional): Specify one or more comma-delimited time periods to return stats for. Defaults to "all_time".
            convert (str, optional): Calculate each market quote in up to 120 currency symbols.
                    Example: "USD,ALL". Defaults to None.
            convert_id (str, optional): Calculate each market quote using CoinMarketCap IDs instead of symbol.
                    Can't be used with convert. Example: "1,2781". Defaults to None.
            skip_invalid (bool, optional): Skip invalid lookups / result. Defaults to False.

        Returns:
            [type]: [description]
        """
        return Response[Dict](
            self.__get(
                "/cryptocurrency/price-performance-stats/latest",
                id=id,
                slug=slug,
                symbol=symbol,
                time_period=time_period,
                convert=convert,
                convert_id=convert_id,
                skip_invalid=skip_invalid,
            )
        )

    def crypto_quotes_historical(
        self,
        id: str = None,
        symbol: str = None,
        time_start: str = None,
        time_end: str = None,
        count: int = 10,
        interval: str = "5m",
        convert: str = None,
        convert_id: str = None,
        aux: str = "price,volume,market_cap,quote_timestamp,is_active,is_fiat",
        skip_invalid: bool = False,
    ) -> Response[Dict]:
        """Returns an interval of historic market quotes for any cryptocurrency based on time and interval parameters.

        Args:
            id (str, optional): One or more comma-separated cryptocurrency CoinMarketCap IDs. Example: 1,2.
                    Defaults to None.
            symbol (str, optional): Alternatively pass one or more comma-separated cryptocurrency symbols.
                    Example: "BTC,ETH". Defaults to None.
            time_start (str, optional): Timestamp (Unix or ISO 8601) to start returning quotes for. Optional,
                    if not passed, we'll return quotes calculated in reverse from "time_end". Defaults to None.
            time_end (str, optional): Timestamp (Unix or ISO 8601) to stop returning quotes for (inclusive). Optional,
                    if not passed, we'll default to the current time. If no "time_start" is passed, we return quotes in reverse order starting from this time. Defaults to None.
            count (int, optional): The number of interval period to return resultst for. Defaults to 10.
            interval (str, optional): Interval of time to return data points for. Valid Values: "yearly" "monthly" "weekly" "daily" "hourly" "5m"
                    "10m" "15m" "30m" "45m" "1h" "2h" "3h" "4h" "6h" "12h" "24h" "1d" "2d" "3d" "7d" "14d" "15d" "30d" "60d" "90d" "365d". Defaults to "5m".
            convert (str, optional): Calculate each market quote in up to 120 currency symbols.
                    Example: "USD,ALL". Defaults to None.
            convert_id (str, optional): Calculate each market quote using CoinMarketCap IDs instead of symbol.
                    Can't be used with convert. Example: "1,2781". Defaults to None.
            aux (str, optional): Comma-separated list of supplemental data fields to return. Defaults to "price,volume,market_cap,quote_timestamp,is_active,is_fiat".
            skip_invalid (bool, optional): Skip invalid lookups / result. Defaults to False.

        Returns:
            [type]: [description]
        """
        return Response[Dict](
            self.__get(
                "/cryptocurrency/quotes/historical",
                id=id,
                symbol=symbol,
                time_start=time_start,
                time_end=time_end,
                count=count,
                interval=interval,
                convert=convert,
                convert_id=convert_id,
                aux=aux,
                skip_invalid=skip_invalid,
            )
        )

    def crypto_quotes_latest(
        self,
        id: str = None,
        slug: str = None,
        symbol: str = None,
        convert: str = None,
        convert_id: str = None,
        aux: str = "num_market_pairs,cmc_rank,date_added,tags,platform,max_supply,circulating_supply,total_supply,is_active,is_fiat",
        skip_invalid: bool = False,
    ) -> Response[Dict]:
        """[summary]

        Args:
            id (str, optional): One or more comma-separated cryptocurrency CoinMarketCap IDs. Example: 1,2.
                    Defaults to None.
            slug (str, optional): Alternatively pass a comma-separated list of cryptocurrency slugs.
                    Example: "bitcoin,ethereum". Defaults to None.
            symbol (str, optional): Alternatively pass one or more comma-separated cryptocurrency symbols.
                    Example: "BTC,ETH". Defaults to None.
            convert (str, optional): Calculate each market quote in up to 120 currency symbols.
                    Example: "USD,ALL". Defaults to None.
            convert_id (str, optional): Calculate each market quote using CoinMarketCap IDs instead of symbol.
                    Can't be used with convert. Example: "1,2781". Defaults to None.
            aux (str, optional): aux (str, optional): Comma-separated list of supplemental data fields to return.
                    Defaults to "num_market_pairs,cmc_rank,date_added,tags,platform,max_supply,circulating_supply,total_supply,is_active,is_fiat".
            skip_invalid (bool, optional): Skip invalid lookups / result. Defaults to False.

        Returns:
            [type]: [description]
        """
        return Response[Dict](
            self.__get(
                "/cryptocurrency/quotes/latest",
                id=id,
                slug=slug,
                symbol=symbol,
                convert=convert,
                convert_id=convert_id,
                aux=aux,
                skip_invalid=skip_invalid,
            )
        )

    def crypto_trending_gainers_losers(
        self,
        start: int = 1,
        limit: int = 100,
        time_period: str = "24h",
        convert: str = None,
        convert_id: str = None,
    ) -> Response[List[Dict]]:
        """Returns a paginated list of all trending cryptocurrencies, determined and sorted by the largest price gains or losses.

        Args:
            start (int, optional): Page to return the result. Defaults to 1.
            limit (int, optional): Limit the number of result. Defaults to 100.
            time_period (str, optional): Adjusts the overall window of time for the biggest gainers and losers.
                    Valid Values: "1h" "24h" "30d" "7d". Defaults to "24h".
            convert (str, optional): Calculate each market quote in up to 120 currency symbols.
                    Example: "USD,ALL". Defaults to None.
            convert_id (str, optional): Calculate each market quote using CoinMarketCap IDs instead of symbol.
                    Can't be used with convert. Example: "1,2781". Defaults to None.

        Returns:
            [type]: [description]
        """
        return Response[List[Dict]](
            self.__get(
                "/cryptocurrency/trending/gainers-losers",
                start=start,
                limit=limit,
                time_period=time_period,
                convert=convert,
                convert_id=convert_id,
            )
        )

    def crypto_trending_latest(
        self,
        start: int = 1,
        limit: int = 100,
        convert: str = None,
        convert_id: str = None,
    ) -> Response[List[Dict]]:
        """Returns a paginated list of all trending cryptocurrency market data, determined and sorted by CoinMarketCap search volume.

        Args:
            start (int, optional): Page to return the result. Defaults to 1.
            limit (int, optional): Limit the number of results. Defaults to 100.
            convert (str, optional): Calculate each market quote in up to 120 currency symbols.
                    Example: "USD,ALL". Defaults to None.
            convert_id (str, optional): Calculate each market quote using CoinMarketCap IDs instead of symbol.
                    Can't be used with convert. Example: "1,2781". Defaults to None.

        Returns:
            [type]: [description]
        """
        return Response[List[Dict]](
            self.__get(
                "/cryptocurrency/trending/latest",
                start=start,
                limit=limit,
                convert=convert,
                convert_id=convert_id,
            )
        )

    def crypto_trending_most_visited(
        self,
        start: int = 1,
        limit: int = 100,
        time_period: str = "24h",
        convert: str = None,
        convert_id: str = None,
    ) -> Response[List[Dict]]:
        """Returns a paginated list of all trending cryptocurrency market data, determined and sorted by traffic to coin detail pages.

        Args:
            start (int, optional): Page to return the result. Defaults to 1.
            limit (int, optional): Limit the number of result. Defaults to 100.
            time_period (str, optional): Adjusts the overall window of time for the biggest gainers and losers.
                    Valid Values: "24h" "30d" "7d". Defaults to "24h".
            convert (str, optional): Calculate each market quote in up to 120 currency symbols.
                    Example: "USD,ALL". Defaults to None.
            convert_id (str, optional): Calculate each market quote using CoinMarketCap IDs instead of symbol.
                    Can't be used with convert. Example: "1,2781". Defaults to None.

        Returns:
            [type]: [description]
        """
        return Response[List[Dict]](
            self.__get(
                "/cryptocurrency/trending/most-visited",
                start=start,
                limit=limit,
                time_period=time_period,
                convert=convert,
                convert_id=convert_id,
            )
        )

    def fiat_map(
        self,
        start: int = 1,
        limit: int = None,
        sort: str = "id",
        include_metals: bool = False,
    ) -> Response[List[Dict]]:
        """Returns a mapping of all supported fiat currencies to unique CoinMarketCap IDs.

        Args:
            start (int, optional): Page to return the result. Defaults to 1.
            limit (int, optional): Limit the number of results. Defaults to None.
            sort (str, optional): Sort the list by. Valid Values: "name" "id". Defaults to "id".
            include_metals (bool, optional): Include precious metals. Defaults to False.

        Returns:
            [type]: [description]
        """
        return Response[List[Dict]](
            self.__get(
                "/fiat/map",
                start=start,
                limit=limit,
                sort=sort,
                include_metals=include_metals,
            )
        )

    def exchange_metadata(
        self,
        id: str = None,
        slug: str = None,
        aux: str = "urls,logo,description,date_launched,notice",
    ) -> Response[Dict]:
        """Returns all static metadata for one or more exchanges.

        Args:
            id (str, optional): One or more comma-separated CoinMarketCap cryptocurrency exchange ids. Example: "1,2".
                    Defaults to None.
            slug (str, optional): One or more comma-separated exchange names in URL friendly shorthand.
                    Defaults to None.
            aux (str, optional): Comma-separated list of supplemental data fields to return.
                    Defaults to "urls,logo,description,date_launched,notice".

        Returns:
            [type]: [description]
        """
        return Response[Dict](self.__get("/exchange/info", id=id, slug=slug, aux=aux))

    def exchange_map(
        self,
        listing_status: str = "active",
        slug: str = None,
        start: int = 1,
        limit: int = None,
        sort: str = "id",
        aux: str = "first_historical_data,last_historical_data,is_active",
        crypto_id: str = "",
    ) -> Response[List[Dict]]:
        """Returns a paginated list of all active cryptocurrency exchanges by CoinMarketCap ID.

        Args:
            listing_status (str, optional): Echange listing status. Accepts comma-separated values.
                Valid Values: "active" "inactive" "untracked". Defaults to "active".
            slug (str, optional): One or more comma-separated exchange names in URL friendly shorthand.
                    Defaults to None.
            start (int, optional): Page to return the result. Defaults to 1.
            limit (int, optional): Limit the number of results. Defaults to None.
            sort (str, optional): Sort the list of exchanges by. Valid Values: "volume_24h" "id".
                    Defaults to "id".
            aux (str, optional): Comma-separated list of supplemental data fields to return.
                    Defaults to "first_historical_data,last_historical_data,is_active".
            crypto_id (str, optional): Include one or cryptocurrency IDs to filter market pairs by. Defaults to "".

        Returns:
            [type]: [description]
        """
        return Response[List[Dict]](
            self.__get(
                "/exchange/map",
                listing_status=listing_status,
                slug=slug,
                start=start,
                limit=limit,
                sort=sort,
                aux=aux,
                crypto_id=crypto_id,
            )
        )

    def exchange_listings_latest(
        self,
        start: int = 1,
        limit: int = 100,
        sort: str = "volume_24h",
        sort_dir: str = None,
        market_type: str = "all",
        category: str = "all",
        aux: str = "num_market_pairs,traffic_score,rank,exchange_score,effective_liquidity_24h",
        convert: str = None,
        convert_id: str = None,
    ) -> Response[List[Dict]]:
        """Returns a paginated list of all cryptocurrency exchanges including the latest aggregate market data for each exchange.

        Args:
            start (int, optional): Page to return the result. Defaults to 1.
            limit (int, optional): Limit the number of results. Defaults to 100.
            sort (str, optional): Sort list of exchanges by. Valid Values: "name" "volume_24h" "volume_24h_adjusted" "exchange_score".
                    Defaults to "volume_24h".
            sort_dir (str, optional): Order the exchanges against the specified sort. Valid Values: "asc" "desc".
                    Defaults to None.
            market_type (str, optional): Type of exchange markets to include in rankings. This field is deprecated. Defaults to "all".
            category (str, optional): Exchange category. Valid Values: "fees" "no_fees" "all".
                    Defaults to "all".
            aux (str, optional): Comma-separated list of supplemental data fields to return.
                    Defaults to "num_market_pairs,traffic_score,rank,exchange_score,effective_liquidity_24h".
            convert (str, optional): Calculate each market quote in up to 120 currency symbols.
                    Example: "USD,ALL". Defaults to None.
            convert_id (str, optional): Calculate each market quote using CoinMarketCap IDs instead of symbol.
                    Can't be used with convert. Example: "1,2781". Defaults to None.

        Returns:
            [type]: [description]
        """
        return Response[List[Dict]](
            self.__get(
                "/exchange/listings/latest",
                start=start,
                limit=limit,
                sort=sort,
                sort_dir=sort_dir,
                market_type=market_type,
                category=category,
                aux=aux,
                convert=convert,
                convert_id=convert_id,
            )
        )

    def exchange_marketpairs_latest(
        self,
        id: str = None,
        slug: str = None,
        start: int = 1,
        limit: int = 100,
        aux: str = "num_market_pairs,category,fee_type",
        matched_id: str = None,
        matched_symbol: str = None,
        category: str = "all",
        fee_type: str = "all",
        convert: str = None,
        convert_id: str = None,
    ) -> Response[Dict]:
        """Returns all active market pairs that CoinMarketCap tracks for a given exchange.

        Args:
            id (str, optional): One or more comma-separated CoinMarketCap cryptocurrency exchange ids. Example: "1,2".
                    Defaults to None.
            slug (str, optional): One or more comma-separated exchange names in URL friendly shorthand.
                    Defaults to None.
            start (int, optional): Page to return the result. Defaults to 1.
            limit (int, optional): Limit the number of results. Defaults to 100.
            aux (str, optional): Comma-separated list of supplemental data fields to return.
                    Defaults to "num_market_pairs,category,fee_type".
            matched_id (str, optional): Include one or more fiat or cryptocurrency IDs to filter market pairs by.
                    Parameter cannot be used with matched_symbol. Defaults to None.
            matched_symbol (str, optional): Include one or more fiat or cryptocurrency symbols to filter market pairs by.
                    Parameter cannot be used with matched_symbol. Defaults to None.
            category (str, optional): The category of trading this market falls under.
                    Valid Values: "all" "spot" "derivatives" "otc" "futures" "perpetual". Defaults to "all".
            fee_type (str, optional): Fee type the exhange enforces this market. Valid Values: "all" "percentage" "no-fees" "transactional-mining" "unknown".
                    Defaults to "all".
            convert (str, optional): Calculate each market quote in up to 120 currency symbols.
                    Example: "USD,ALL". Defaults to None.
            convert_id (str, optional): Calculate each market quote using CoinMarketCap IDs instead of symbol.
                    Can't be used with convert. Example: "1,2781". Defaults to None.

        Returns:
            [type]: [description]
        """
        return Response[Dict](
            self.__get(
                "/exchange/market-pairs/latest",
                id=id,
                slug=slug,
                start=start,
                limit=limit,
                aux=aux,
                matched_id=matched_id,
                matched_symbol=matched_symbol,
                category=category,
                fee_type=fee_type,
                convert=convert,
                convert_id=convert_id,
            )
        )

    def exchange_quotes_historical(
        self,
        id: str = None,
        slug: str = None,
        time_start: str = None,
        time_end: str = None,
        count: float = 10,
        interval: str = "5m",
        convert: str = None,
        convert_id: str = None,
    ) -> Response[Dict]:
        """Returns an interval of historic quotes for any exchange based on time and interval parameters.

        Args:
            id (str, optional): One or more comma-separated CoinMarketCap cryptocurrency exchange ids. Example: "1,2".
                    Defaults to None.
            slug (str, optional): One or more comma-separated exchange names in URL friendly shorthand.
                    Defaults to None.
            time_start (str, optional): Timestamp (Unix or ISO 8601) to start returning quotes for. Optional,
                    if not passed, we'll return quotes calculated in reverse from "time_end". Defaults to None.
            time_end (str, optional): Timestamp (Unix or ISO 8601) to stop returning quotes for (inclusive).
                    Optional, if not passed, we'll default to the current time. If no "time_start" is passed,
                    we return quotes in reverse order starting from this time. Defaults to None.
            count (int, optional): Limit the number of results. Defaults to 10.
            interval (str, optional): [description]. Valid Values: "hourly" "daily" "weekly" "monthly" "yearly" "1h" "2h" "3h" "4h" "6h" "12h"
                    "1d" "2d" "3d" "7d" "14d" "15d" "30d" "60d" "90d" "365d".
                    Defaults to "5m".
            convert (str, optional): Calculate each market quote in up to 120 currency symbols.
                    Example: "USD,ALL". Defaults to None.
            convert_id (str, optional): Calculate each market quote using CoinMarketCap IDs instead of symbol.
                    Can't be used with convert. Example: "1,2781". Defaults to None.

        Returns:
            [type]: [description]
        """
        return Response[Dict](
            self.__get(
                "/exchange/quotes/historical",
                id=id,
                slug=slug,
                time_start=time_start,
                time_end=time_end,
                count=count,
                interval=interval,
                convert=convert,
                convert_id=convert_id,
            )
        )

    def exchange_quotes_latest(
        self,
        id: str = None,
        slug: str = None,
        convert: str = None,
        convert_id: str = None,
        aux: str = "num_market_pairs,traffic_score,rank,exchange_score,liquidity_score,effective_liquidity_24h",
    ) -> Response[Dict]:
        """Returns the latest aggregate market data for 1 or more exchanges.[summary]

        Args:
            id (str, optional): One or more comma-separated CoinMarketCap cryptocurrency exchange ids. Example: "1,2".
                    Defaults to None.
            slug (str, optional): One or more comma-separated exchange names in URL friendly shorthand.
                    Defaults to None.
            convert (str, optional): Calculate each market quote in up to 120 currency symbols.
                    Example: "USD,ALL". Defaults to None.
            convert_id (str, optional): Calculate each market quote using CoinMarketCap IDs instead of symbol.
                    Can't be used with convert. Example: "1,2781". Defaults to None.
            aux (str, optional): Comma-separated list of supplemental data fields to return.
                    Defaults to "num_market_pairs,traffic_score,rank,exchange_score,liquidity_score,effective_liquidity_24h".

        Returns:
            [type]: [description]
        """
        return Response[Dict](
            self.__get(
                "/exchange/quotes/latest",
                id=id,
                slug=slug,
                convert=convert,
                convert_id=convert_id,
                aux=aux,
            )
        )

    def globalmetrics_quotes_historical(
        self,
        time_start: str = None,
        time_end: str = None,
        count: int = 10,
        interval: str = "1d",
        convert: str = None,
        convert_id: str = None,
        aux: str = "btc_dominance,active_cryptocurrencies,active_exchanges,active_market_pairs,total_volume_24h,total_volume_24h_reported,altcoin_market_cap,altcoin_volume_24h,altcoin_volume_24h_reported",
    ) -> Response[List[Dict]]:
        """Returns an interval of historical global cryptocurrency market metrics based on time and interval parameters.

        Args:
            time_start (str, optional): Timestamp (Unix or ISO 8601) to start returning quotes for. Optional,
                    if not passed, we'll return quotes calculated in reverse from "time_end". Defaults to None.
            time_end (str, optional): Timestamp (Unix or ISO 8601) to stop returning quotes for (inclusive).
                    Optional, if not passed, we'll default to the current time. If no "time_start" is passed,
                    we return quotes in reverse order starting from this time. Defaults to None.
            count (int, optional): Limit the number of results. Defaults to 10.
            interval (str, optional): [description]. Valid Values: "hourly" "daily" "weekly" "monthly" "yearly" "1h" "2h" "3h" "4h" "6h" "12h"
                    "1d" "2d" "3d" "7d" "14d" "15d" "30d" "60d" "90d" "365d".
                    Defaults to "5m".
            convert (str, optional): Calculate each market quote in up to 120 currency symbols.
                    Example: "USD,ALL". Defaults to None.
            convert_id (str, optional): Calculate each market quote using CoinMarketCap IDs instead of symbol.
                    Can't be used with convert. Example: "1,2781". Defaults to None.
            aux (str, optional): Comma-separated list of supplemental data fields to return.
                    Defaults to "btc_dominance,active_cryptocurrencies,active_exchanges,active_market_pairs,total_volume_24h,total_volume_24h_reported,altcoin_market_cap,altcoin_volume_24h,altcoin_volume_24h_reported".

        Returns:
            [type]: [description]
        """
        return Response[List[Dict]](
            self.__get(
                "/global-metrics/quotes/historical",
                time_start=time_start,
                time_end=time_end,
                count=count,
                interval=interval,
                convert=convert,
                convert_id=convert_id,
                aux=aux,
            )
        )

    def globalmetrics_quotes_latest(
        self, convert: str = None, convert_id: str = None
    ) -> Response[Dict]:
        """Comma-separated list of supplemental data fields to return.[summary]

        Args:
            convert (str, optional): Calculate each market quote in up to 120 currency symbols.
                    Example: "USD,ALL". Defaults to None.
            convert_id (str, optional): Calculate each market quote using CoinMarketCap IDs instead of symbol.
                    Can't be used with convert. Example: "1,2781". Defaults to None.

        Returns:
            [type]: [description]
        """

        return Response[Dict](
            self.__get(
                "/global-metrics/quotes/latest", convert=convert, convert_id=convert_id
            )
        )

    def tools_price_conversion(
        self,
        amount: float,
        id: str = None,
        symbol: str = None,
        time: str = None,
        convert: str = None,
        convert_id: str = None,
    ) -> Response[Dict]:
        """Convert an amount of one cryptocurrency or fiat currency into one or more different currencies utilizing the latest market rate for each currency.

        Args:
            amount (float): The amount of currency to convert.
            id (str, optional): CoinMarketCap currency ID of the base cryptocurrency or fiat to convert from. Defaults to None.
            symbol (str, optional): CoinMarketCap currency ID of the base cryptocurrency or fiat to convert from. Defaults to None.
            time (str, optional): Optional timestamp (Unix or ISO 8601) to reference historical pricing during conversion. If not
                    passed, the current time will be used. If passed, we'll reference the closest historic values available for this
                    conversion. Defaults to None.
            convert (str, optional): Calculate each market quote in up to 120 currency symbols.
                    Example: "USD,ALL". Defaults to None.
            convert_id (str, optional): Calculate each market quote using CoinMarketCap IDs instead of symbol.
                    Can't be used with convert. Example: "1,2781". Defaults to None.

        Returns:
            [type]: [description]
        """
        return Response[Dict](
            self.__get(
                "/tools/price-conversion",
                amount=amount,
                id=id,
                symbol=symbol,
                time=time,
                convert=convert,
                convert_id=convert_id,
            )
        )

    def blockchain_statistics_latest(
        self, id: str = None, symbol: str = None, slug: str = None
    ) -> Response[Dict]:
        """Returns the latest blockchain statistics data for 1 or more blockchains. Bitcoin, Litecoin, and Ethereum are currently supported.

        Args:
            id (str, optional): One or more comma-separated CoinMarketCap cryptocurrency IDs.
                    Example: "1,2". Defaults to None.
            symbol (str, optional): Comma-separated cryptocurrency symbols. Example: "BTC,ETH".
                    Defaults to None.
            slug (str, optional): Comma-separated cryptocurrency slugs. Example: "bitcoin,ethereum".
                    Defaults to None.

        Returns:
            [type]: [description]
        """
        return Response[Dict](
            self.__get("/blockchain/statistics/latest", id=id, symbol=symbol, slug=slug)
        )

    def partners_fsc_fcas_listings_latest(
        self,
        start: int = 1,
        limit: int = 100,
        aux: str = "point_change_24h,percent_change_24h",
    ) -> Response[List[Dict]]:
        """Returns a paginated list of FCAS scores for all cryptocurrencies currently supported by FCAS.

        Args:
            start (int, optional): Page to return the result. Defaults to 1.
            limit (int, optional): Limit the number of result. Defaults to 100.
            aux (str, optional): Comma-separated list of supplemental data fields to return.
                Defaults to "point_change_24h,percent_change_24h".

        Returns:
            [type]: [description]
        """
        return Response[List[Dict]](
            self.__get(
                "/partners/flipside-crypto/fcas/listings/latest",
                start=start,
                limit=limit,
                aux=aux,
            )
        )

    def partners_fsc_fcas_lquotes_latest(
        self,
        id: str = None,
        slug: str = None,
        symbol: str = None,
        aux: str = "point_change_24h,percent_change_24h",
    ) -> Response[Dict]:
        """Returns the latest FCAS score for 1 or more cryptocurrencies. FCAS ratings are on a
        0-1000 point scale with a corresponding letter grade and is updated once a day at UTC midnight.

        Args:
            id (str, optional): One or more comma-separated CoinMarketCap cryptocurrency IDs.
                    Example: "1,2". Defaults to None.
            symbol (str, optional): Comma-separated cryptocurrency symbols. Example: "BTC,ETH".
                    Defaults to None.
            slug (str, optional): Comma-separated cryptocurrency slugs. Example: "bitcoin,ethereum".
                    Defaults to None.
            aux (str, optional): Comma-separated list of supplemental data fields to return.
                    Defaults to "point_change_24h,percent_change_24h".

        Returns:
            [type]: [description]
        """
        return Response[Dict](
            self.__get(
                "/partners/flipside-crypto/fcas/quotes/latest",
                slug=slug,
                symbol=symbol,
                id=id,
                aux=aux,
            )
        )

    def key_info(self) -> Response[Dict]:
        """Returns API key details and usage stats. This endpoint can be used to programmatically monitor your
        key usage compared to the rate limit and daily/monthly credit limits available to your API plan.

        Returns:
            [type]: [description]
        """
        return Response[Dict](self.__get("/key/info"))
