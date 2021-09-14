import asyncio
import time
from datetime import datetime

from . import BaseAPI


class UnofficialAPI(BaseAPI):
    """
    Unofficial API wrapper class for TipRanks.com.
    Unofficial means this class calls some hidden endpoints
    and provides data that official API doesn't. Also doesn't
    need an authorization.
    """

    def get_dividends(self):
        """
        Fetches symbol dividends with following fields:

        * yield
        * amount
        * payment_date
        * ex_date
        * receive_date
        * growth_since

        :return: List of dividend objects.
        :rtype: list
        """

        response = self._get(
            f"https://tr-frontend-cdn.azureedge.net/bff/prod/stock/{self.symbol.lower()}/payload.json",
        )
        data = response.json()

        dividends = []

        if data["dividend"]["history"]:
            for item in data["dividend"]["history"]:
                dividends.append(
                    {
                        "yield": float(item["yield"]),
                        "amount": float(item["amount"]),
                        "payment_date": datetime.strptime(
                            item["payDate"], "%Y-%m-%dT%H:%M:%S.000Z"
                        ).date(),
                        "ex_date": datetime.strptime(
                            item["executionDate"], "%Y-%m-%dT%H:%M:%S.000Z"
                        ).date(),
                        "receive_date": datetime.strptime(
                            item["recordDate"], "%Y-%m-%dT%H:%M:%S.000Z"
                        ).date(),
                        "growth_since": datetime.strptime(
                            item["growthSince"], "%Y-%m-%dT%H:%M:%S.000Z"
                        ),
                    }
                )

        return dividends

    def get_basic_info(self):
        """
        Downloads basic info. Data are:

        * company_name
        * market
        * description
        * market_cap
        * has_dividends
        * yoy_change
        * year_low
        * year_high
        * pe_ratio
        * eps
        * similar_stocks
            * ticker
            * company_name

        :return: Dict with data.
        :rtype: dict
        """

        async def download_basics(symbol):
            """
            Downloads basic info about symbol. Data are:

            * company_name
            * market
            * description
            * market_cap
            * has_dividends
            * similar_stocks
                * ticker
                * company_name
            * yoy_change

            :param str symbol: Symbol the data will be downloaded for.
            :return: Dict with data.
            :rtype: dict
            """

            data = await self._aget(
                f"https://tr-frontend-cdn.azureedge.net/bff/prod/stock/{symbol.lower()}/payload.json"
            )
            json_data = data.json()

            data = {
                "company_name": json_data["common"]["stock"]["fullName"],
                "market": json_data["common"]["stock"]["market"],
                "description": json_data["common"]["stock"]["description"],
                "market_cap": int(json_data["common"]["stock"]["marketCap"]),
                "has_dividends": bool(
                    json_data["common"]["stock"]["dividend"].get("yield", False)
                ),
                "yoy_change": float(
                    json_data["common"]["stock"]["technical"]["momentum"][
                        "twelveMonths"
                    ]
                )
                * 100,
                "year_low": json_data["common"]["stock"]["priceRange"]["last52Week"][
                    "low"
                ],
                "year_high": json_data["common"]["stock"]["priceRange"]["last52Week"][
                    "high"
                ],
                "pe_ratio": json_data["common"]["stock"]["pe"],
                "eps": json_data["common"]["stock"]["earning"]["espYear"],
                "similar_stocks": [],
            }

            if json_data["similar"]["similar"]:
                for stock in json_data["similar"]["similar"]:
                    data["similar_stocks"].append(
                        {"ticker": stock["ticker"], "company_name": stock["name"]}
                    )

            return data

        async def download_additionals(symbol):
            """
            Downloads additional info. Data are:

            * year_low
            * year_high
            * pe_ratio
            * eps

            :param str symbol: Symbol the data will be downloaded for.
            :return: Dict with data.
            :rtype: dict
            """

            data = await self._aget(
                f"https://market.tipranks.com/api/details/GetRealTimeQuotes/?tickers={symbol}"
            )
            json_data = data.json()

            return {
                "year_low": json_data[0]["yLow"],
                "year_high": json_data[0]["yHigh"],
                "pe_ratio": json_data[0]["pe"],
                "eps": json_data[0]["eps"],
            }

        async def main():

            basic, additionals = await asyncio.gather(
                download_basics(self.symbol), download_additionals(self.symbol)
            )
            basic.update(additionals)

            return basic

        return asyncio.run(main())
