#!/usr/bin/python
"""Bitfinex Rest API V2 implementation"""
# pylint: disable=R0904

from __future__ import absolute_import
import json
from json.decoder import JSONDecodeError
import hmac
import hashlib
import requests
from bitfinex import utils
from enum import Enum

PROTOCOL = "https"
PUBLIC_PREFIX = "api-pub"
PRIVATE_PREFIX = "api"
HOST = "bitfinex.com"
VERSION = "v2"


# HTTP request timeout in seconds
TIMEOUT = 5.0
LOGGER = utils.get_bitfinex_logger(__name__)

class BitfinexException(Exception):
    """
    Exception handler
    """
    pass

class Client:
    """Client for the bitfinex.com API REST V2.
    Link for official bitfinex documentation :

    `Bitfinex rest2 docs <https://docs.bitfinex.com/docs>`_

    `Bitfinex rest2 reference <https://docs.bitfinex.com/reference>`_

    Parameters
    ----------
    key : str
        Bitfinex api key

    secret : str
        Bitfinex api secret

    nonce_multiplier : Optional float
        Multiply nonce by this number

    Examples
    --------
     ::

        bfx_client = Client(key,secret)

        bfx_client = Client(key,secret,2.0)
    """

    def __init__(self, key=None, secret=None, nonce_multiplier=1.0, proxy=None):
        """
        Object initialisation takes 2 mandatory arguments key and secret and a optional one
        nonce_multiplier
        """

        assert isinstance(nonce_multiplier, float), "nonce_multiplier must be decimal"
        self.private_url = "%s://%s.%s/" % (PROTOCOL, PRIVATE_PREFIX, HOST)
        self.public_url = "%s://%s.%s/" % (PROTOCOL, PUBLIC_PREFIX, HOST)
        self.key = key
        self.secret = secret
        self.nonce_multiplier = nonce_multiplier
        self.proxy = proxy

    def _nonce(self):
        """Returns a nonce used in authentication.
        Nonce must be an increasing number, if the API key has been used
        earlier or other frameworks that have used higher numbers you might
        need to increase the nonce_multiplier."""
        return str(utils.get_nonce(self.nonce_multiplier))

    def _headers(self, path, nonce, body):
        """
        create signed headers
        """
        signature = "/api/{}{}{}".format(path, nonce, body)
        hmc = hmac.new(self.secret.encode('utf8'), signature.encode('utf8'), hashlib.sha384)
        signature = hmc.hexdigest()

        return {
            "bfx-nonce": nonce,
            "bfx-apikey": self.key,
            "bfx-signature": signature,
            "content-type": "application/json"
        }

    def _post(self, path, payload, verify=False):
        """
        Send post request to bitfinex
        """
        nonce = self._nonce()
        headers = self._headers(path, nonce, payload)
        response = requests.post(self.private_url + path, headers=headers, data=payload, verify=verify, proxies=self.proxy)

        if response.status_code == 200:
            return response.json()
        else:
            try:
                content = response.json()
            except JSONDecodeError:
                content = response.text
            raise BitfinexException(response.status_code, response.reason, content)

    def _public_post(self, path, payload, verify=False):
        """
        Send post request to bitfinex
        """
        response = requests.post(self.public_url + path, data=payload, verify=verify, proxies=self.proxy)

        if response.status_code == 200:
            return response.json()
        else:
            try:
                content = response.json()
            except JSONDecodeError:
                content = response.text
            raise BitfinexException(response.status_code, response.reason, content)

    def _get(self, path, **params):
        """
        Send get request to bitfinex
        """
        url = self.public_url + path
        response = requests.get(url, timeout=TIMEOUT, params=params, proxies=self.proxy)
        if response.status_code == 200:
            return response.json()
        else:
            try:
                content = response.json()
            except JSONDecodeError:
                content = response.text
            raise BitfinexException(response.status_code, response.reason, content)

    # REST PUBLIC ENDPOINTS
    def platform_status(self):
        """
        .. _platform_status:

        `Bitfinex platform_status reference
        <https://docs.bitfinex.com/reference#rest-public-platform-status>`_

        Get the current status of the platform. Maintenance periods last for just few minutes and
        might be necessary from time to time during upgrades of core components of our
        infrastructure. Even if rare it is important to have a way to notify users. For a real-time
        notification we suggest to use websockets and listen to events 20060/20061

        Returns
        -------
        int
            - 1 = operative
            - 0 = maintenance

        Example
        -------
         ::

            bfx_client.platform_status()

        """
        path = "v2/platform/status"
        response = self._get(path)
        return response

    def tickers(self, symbol_list):
        """`Bitfinex tickers reference
        <https://docs.bitfinex.com/reference#rest-public-tickers>`_

        The ticker is a high level overview of the state of the market. It shows you the current
        best bid and ask, as well as the last trade price.It also includes information such as daily
        volume and how much the price has moved over the last day.

        Parameters
        ----------
        symbol_list : list
            The symbols you want information about as a comma separated list,
            or ALL for every symbol.

        Returns
        -------
        list
             ::

                [
                  # on trading pairs (ex. tBTCUSD)
                  [
                    SYMBOL,
                    BID,
                    BID_SIZE,
                    ASK,
                    ASK_SIZE,
                    DAILY_CHANGE,
                    DAILY_CHANGE_PERC,
                    LAST_PRICE,
                    VOLUME,
                    HIGH,
                    LOW
                  ],
                  # on funding currencies (ex. fUSD)
                  [
                    SYMBOL,
                    FRR,
                    BID,
                    BID_SIZE,
                    BID_PERIOD,
                    ASK,
                    ASK_SIZE,
                    ASK_PERIOD,
                    DAILY_CHANGE,
                    DAILY_CHANGE_PERC,
                    LAST_PRICE,
                    VOLUME,
                    HIGH,
                    LOW
                  ],
                  ...
                ]

        Note
        ----
            ================= ===== ================================================================
            Field             Type  Description
            ================= ===== ================================================================
            FRR               float Flash Return Rate - average of all fixed rate funding over the
                                    last hour
            BID               float Price of last highest bid
            BID_PERIOD        int   Bid period covered in days
            BID_SIZE          float Sum of the 25 highest bid sizes
            ASK               float Price of last lowest ask
            ASK_PERIOD        int   Ask period covered in days
            ASK_SIZE          float Sum of the 25 lowest ask sizes
            DAILY_CHANGE      float Amount that the last price has changed since yesterday
            DAILY_CHANGE_PERC float Amount that the price has changed expressed in percentage terms
            LAST_PRICE        float Price of the last trade
            VOLUME            float Daily volume
            HIGH              float Daily high
            LOW               float Daily low
            ================= ===== ================================================================

        Examples
        --------
         ::

            bfx_client.tickers(['tIOTUSD', 'fIOT'])
            bfx_client.tickers(['tBTCUSD'])
            bfx_client.tickers(['ALL'])

        """
        assert isinstance(symbol_list, list), "symbol_list must be of type list"
        assert symbol_list, "symbol_list must have at least one symbol"
        path = "v2/tickers?symbols={}".format(",".join(symbol_list))
        response = self._get(path)
        return response

    def ticker(self, symbol):
        """`Bitfinex ticker reference
        <https://docs.bitfinex.com/reference#rest-public-ticker>`_

        The ticker is a high level overview of the state of the market.It shows you the current best
        bid and ask, as well as the last trade price.It also includes information such as daily
        volume and how much the price has moved over the last day.

        Parameters
        ----------
        symbol : str
            The symbol you want information about.
            You can find the list of valid symbols by calling the `symbols <restv1.html#symbols>`_
            method

        Returns
        -------
        list
             ::

                # on trading pairs (ex. tBTCUSD)
                [
                  BID,
                  BID_SIZE,
                  ASK,
                  ASK_SIZE,
                  DAILY_CHANGE,
                  DAILY_CHANGE_PERC,
                  LAST_PRICE,
                  VOLUME,
                  HIGH,
                  LOW
                ]
                # on funding currencies (ex. fUSD)
                [
                  FRR,
                  BID,
                  BID_SIZE,
                  BID_PERIOD,
                  ASK,
                  ASK_SIZE,
                  ASK_PERIOD,
                  DAILY_CHANGE,
                  DAILY_CHANGE_PERC,
                  LAST_PRICE,
                  VOLUME,
                  HIGH,
                  LOW
                ]

        Examples
        --------
         ::

            bfx_client.ticker('tIOTUSD')
            bfx_client.ticker('fIOT')
            bfx_client.ticker('tBTCUSD')

        """
        path = "v2/ticker/{}".format(symbol)
        response = self._get(path)
        return response

    def trades(self, symbol, **kwargs):
        """`Bitfinex trades reference
        <https://docs.bitfinex.com/reference#rest-public-trades>`_

        The trades endpoint allows the retrieval of past public trades and includes details such as
        price, size, and time. Optional parameters can be used to limit the number of results;
        you can specify a start and end timestamp, a limit, and a sorting method.

        Parameters
        ----------
        symbol : str
            The symbol you want information about.
            You can find the list of valid symbols by calling the `symbols <restv1.html#symbols>`_
            method

        start : string
            Millisecond start time for /hist ( ex : 1568123933000)

        end : string
            Millisecond end time for /hist   (ex : 1570578740000)

        sort : 
            set to 1 for oldest > newest records , -1 for reverse

        limit : 
            Limit of retrieved records. (Max: 10000)

        Returns
        -------
        list
             ::

                // on trading pairs (ex. tBTCUSD)
                [
                  [
                    ID,
                    MTS,
                    AMOUNT,
                    PRICE
                  ]
                ]

                // on funding currencies (ex. fUSD)
                [
                  [
                    ID,
                    MTS,
                    AMOUNT,
                    RATE,
                    PERIOD
                  ]
                ]

                //trading
                [[388063448,1567526214876,1.918524,10682]]

                //funding
                [[124486873,1567526287066,-210.69675707,0.00034369,2]]

        Examples
        --------
         ::

            bfx_client.trades('tIOTUSD')
            bfx_client.trades('fIOT')
            bfx_client.trades('tBTCUSD', limit=1, sort=-1)

        """

        params="?"
        for key, value in kwargs.items():
            params = f"{params}{key}={value}&"
        params = params[:-1] # remove last & or ? if there are no optional parameters 

        path = "v2/trades/{}/hist{}".format(symbol,params)
        response = self._get(path)
        return response

    def book(self, symbol, precision="P0", **kwargs):
        """`Bitfinex book reference
        <https://docs.bitfinex.com/reference#rest-public-book>`_

        The Order Book channel allow you to keep track of the state of the Bitfinex order book.
        It is provided on a price aggregated basis, with customizable precision.

        Parameters
        ----------
        symbol : str
            The `symbol <restv1.html#symbols>`_ you want information about.

        precision : Optional str
            Level of price aggregation (P0, P1, P2, P3, R0).
            R0 means "gets the raw orderbook".

        len : Optional str
            Number of price points ("1", "25", "100")

        Returns
        -------
        list
             ::

                // on trading pairs (ex. tBTCUSD)
                [
                  [
                    PRICE,
                    COUNT,
                    AMOUNT
                  ],
                  ...
                ]

                // on funding currencies (ex. fUSD)
                [
                  [
                    RATE,
                    PERIOD,
                    COUNT,
                    AMOUNT
                  ],
                  ...
                ]

                // on raw books (precision of R0)
                // on trading currencies:
                [
                  [
                    ORDER_ID,
                    PRICE,
                    AMOUNT
                  ],
                  ...
                ]

                // on funding currencies:

                [
                  [
                    ORDER_ID,
                    PERIOD,
                    RATE,
                    AMOUNT
                  ],
                  ...
                ]

                //trading
                [[8744.9,2,0.45603413],[8745,8,-3.64426815]]

                //funding
                [[0.0003301,30,1,-3862.874],[0.00027999,2,2,1843.05088178]]

                //raw books

                //trading
                [[34006738527,8744.9,0.25603413],[34005496171,8745,-0.2]]

                //funding
                [[645902785,30,0.0003301,-3862.874],[649139359,2,0.0003168747915,52.36]]

        Examples
        --------
         ::

            bfx_client.book('tIOTUSD')
            bfx_client.book('fIOT')
            bfx_client.book('tBTCUSD')

        """
        params="?"
        for key, value in kwargs.items():
            params = f"{params}{key}={value}&"
        params = params[:-1] # remove last & or ? if there are no optional parameters 

        path = "v2/book/{}/{}{}".format(symbol, precision, params)
        response = self._get(path)
        return response

    def stats(self, key, size, symbol, side="", section="last", **kwargs):
        """`Bitfinex stats reference
        <https://docs.bitfinex.com/reference#rest-public-stats>`_

        Various statistics about the requested pair.

        Parameters
        ----------
        Key : str
            Allowed values: "funding.size", "credits.size", "credits.size.sym",
            "pos.size"

        Size : str
            Available values: '1m'

        Symbol : str
            The symbol you want information about.

        Side : str
            Available values: "long", "short"

        Section : str
            Available values: "last", "hist"

        start : Options str
            Millisecond start time for /hist ( ex : 1568123933000)

        end : Options str
            Millisecond end time for /hist   (ex : 1570578740000)

        sort : Options str
            set to 1 for oldest > newest records , -1 for reverse

        limit : Options str
            Limit of retrieved records. (Max: 10000)

        Returns
        -------
        list
             ::

                // response with Section = "last"
                [ 
                  MTS,
                  VALUE
                ]
                
                // response with Section = "hist"
                [
                  [
                   MTS,
                   VALUE 
                  ],
                  ...
                ]
                
                //pos size
                [[1573554000000,25957.94278561],[1573553940000,25964.29056204]]
                
                //funding size
                [[1573560420000,374049888.4504578],[1573560360000,373962908.58560276]]
                
                //credits size
                [[1573560420000,369005353.5945115],[1573560360000,368918780.2238935]]
                
                //credits size sym
                [[1573560480000,141144084.0479222],[1573560420000,141144084.0479222]]

        Examples
        --------
         ::

            bfx_client.stats('funding.size', '1m', 'fUSD', section="hist", limit=1)
            bfx_client.stats('pos.size', '1m', 'tBTCUSD', side="long", section="hist", limit=1)
            bfx_client.stats('credits.size', '1m', 'fUSD', section="hist", limit=1)
            bfx_client.stats('credits.size.sym', '1m', 'fUSD:tBTCUSD', section="hist", limit=1)

        """
        side = f":{side}" if side else ""
        path = f"v2/stats1/{key}:{size}:{symbol}{side}/{section}"

        params="?"
        for key, value in kwargs.items():
            params = f"{params}{key}={value}&"
        params = params[:-1]
        path = path + params

        response = self._get(path)
        return response

    def candles(self, timeframe, symbol, section, period="", **kwargs):
        """`Bitfinex candles reference
        <https://docs.bitfinex.com/reference#rest-public-candles>`_

        Provides a way to access charting candle info

        Parameters
        ----------
        timeframe : str
            Available values: '1m', '5m', '15m', '30m', '1h', '3h', '6h', '12h',
            '1D', '7D', '14D', '1M'

        symbol : str
            The symbol you want information about. (eg : tBTCUSD, tETHUSD, fUSD, fBTC)

        section : str
            Available values: "last", "hist"

        period : str
            Funding period. Only required for funding candles. 
            Enter after the symbol (trade:1m:fUSD:p30/hist).

        limit : int
            Number of candles requested (Max: 10000)

        start : str
            Filter start (ms)

        end : str
            Filter end (ms)

        sort : int
            if = 1 it sorts results returned with old > new

        Returns
        -------
        list
             ::

                # response with Section = "last"
                [ MTS, OPEN, CLOSE, HIGH, LOW, VOLUME ]

                # response with Section = "hist"
                [
                  [ MTS, OPEN, CLOSE, HIGH, LOW, VOLUME ],
                  ...
                ]

        Examples
        --------
         ::

            # 1 minute candles
            bfx_client.candles("1m", "tBTCUSD", "hist")

            # 1 hour candles , limit to 1 candle
            bfx_client.candles("1h", "tBTCUSD", "hist", limit='1')
            bfx_client.candles("1h", "tBTCUSD", "last")

            # funding candles

            bfx_client.candles("1m", "fUSD", "hist", period="p30", limit=1)

        """
        period = f":{period}" if period else ""
        path = f"v2/candles/trade:{timeframe}:{symbol}{period}/{section}"

        params="?"
        for key, value in kwargs.items():
            params = f"{params}{key}={value}&"
        path = path + params[:-1]

        response = self._get(path)
        return response


    def configs(self, action : str, obj=None, detail=None):
        """`Bitfinex configs reference
        <https://docs.bitfinex.com/reference#rest-public-conf>`_

        Fetch currency and symbol site configuration data.

        A variety of types of config data can be fetched by constructing a path with an Action, Object, and conditionally a Detail value.

        Multiple sets of parameters may be passed, in a single request, to fetch multiple parts of the sites currency and symbol configuration data.

        Parameters
        ----------
        action : str
            Valid action values: : 'map', 'list', 'info', 'fees'

        Object : str
            Valid object values for the map action: 'currency', 'tx'.

            Valid object values for the list action: 'currency', 'pair', 'competitions'.

            Valid object values for the info action: 'pair'

            Valid object values for the fees action: none

        Detail : str
            The detail parameter is only required for the below action:object values:

            A map:currency request requires one of the following detail values: 
            'sym', 'label', 'unit', 'undl', 'pool', 'explorer'.

            A map:tx request requires the following detail value: 'method'.

            A list:pair request requires one of the following detail values:
            'exchange', 'margin'

        Returns
        -------
        list
             ::

                []

        Examples
        --------
         ::

            bfx_client.configs("fees")
            bfx_client.configs("map","currency","sym")

        """
        path = f"v2/conf/pub:{action}"
        if obj:
            path = f'{path}:{obj}'
        if detail:
            path = f'{path}:{detail}'

        response = self._get(path)
        return response

    def configs_list(self, cfg_list : list):
        """`Bitfinex configs reference
        <https://docs.bitfinex.com/reference#rest-public-conf>`_

        Instead of performing a request for each configuration item it is possible to fetch
        multiple configurations in a single request.

        Parameters
        ----------
        cfg_list : list
            Contains a list of dictionaries that have the following keys : action, obj, detail

        Returns
        -------
        list
             ::

                []

        Examples
        --------
         ::

            bfx_client = Client("key", "secret")
            cfgs = [
                {
                    "action": "fees"
                },
                {
                    "action": "map",
                    "obj": "currency",
                    "detail": "sym"
                }
            ]

            bfx_client.configs_list(cfgs)

        """
        cfg_params = []
        for cfg in cfg_list:
            request = f"pub:{cfg['action']}"
            if 'obj' in cfg:
                request = f"{request}:{cfg['obj']}"
            if 'detail' in cfg:
                request = f"{request}:{cfg['detail']}"
            cfg_params.append(request)


        path = f"v2/conf/{','.join(cfg_params)}" 
        LOGGER.info(path)
        response = self._get(path)
        return response

    def status(self, status_type, keys, **kwargs):
        """`Bitfinex status reference
        <https://docs.bitfinex.com/reference#rest-public-status>`_

        Endpoint used to receive different types of platform information 
        - currently supports derivatives pair status only.

        Parameters
        ----------
        status_type : string
            Path parameter. The status message type. Valid values: deriv

        keys : string
            The key or keys (Separate by commas) of the pairs to fetch status information.
            To fetch information for all pairs use the key value 'ALL',
            (ex: tBTCF0:USTF0 or tETHF0:USTF0)

        start : string
            Millisecond start time for /hist ( ex : 1568123933000)

        end : string
            Millisecond end time for /hist   (ex : 1570578740000)

        sort : 
            set to 1 for oldest > newest records , -1 for reverse

        limit : 
            Limit of retrieved records. (Max: 10000)

        Returns
        -------
        list
             ::

                [
                  [
                    KEY,
                    MTS,
                    PLACEHOLDER, 
                    DERIV_PRICE,
                    SPOT_PRICE,
                    PLACEHOLDER,
                    INSURANCE_FUND_BALANCE,
                    PLACEHOLDER,
                    NEXT_FUNDING_EVT_TIMESTAMP_MS,
                    NEXT_FUNDING_ACCRUED,
                    NEXT_FUNDING_STEP,
                    PLACEHOLDER,
                    CURRENT_FUNDING,
                    PLACEHOLDER,
                    PLACEHOLDER,
                    MARK_PRICE,
                    PLACEHOLDER,
                    PLACEHOLDER,
                    OPEN_INTEREST
                  ]
                ]

        Examples
        --------
         ::

            bfx_client.status("deriv","ALL")

            bfx_client.status("deriv","tBTCF0:USTF0")

            bfx_client.status("deriv", "tBTCF0:USTF0",start="1580020000000",end="1580058375000")


        """

        path = f"v2/status/{status_type}?keys={keys}"

        params="?"
        for key, value in kwargs.items():
            params = f"{params}{key}={value}&"
        params = params[:-1]
        if params:
            path = f"v2/status/{status_type}/{keys}/hist{params}"
        LOGGER.info(path)
        response = self._get(path)
        return response

    def liquidation_feed(self, **kwargs):
        """`Bitfinex Liquidation Feed reference
        <https://docs.bitfinex.com/reference#rest-public-liquidations>`_

        Endpoint to retrieve liquidations. By default it will retrieve the most recent liquidations,
        but time-specific data can be retrieved using timestamps.

        Parameters
        ----------
        start : Optional int
            Millisecond start time

        end : Optional int
            Millisecond end time

        limit : Optional int
            Number of records (Max: 10000)

        sort : Optional int
            if = 1 it sorts results returned with old > new

        Returns
        -------
        list
             ::

                [
                 [
                  ['pos',
                   POS_ID,
                   MTS,
                   PLACEHOLDER,
                   SYMBOL,
                   AMOUNT,
                   BASE_PRICE,
                   PLACEHOLDER,
                   IS_MATCH,
                   IS_MARKET_SOLD,
                   PLACEHOLDER,
                   PRICE_ACQUIRED],
                  ['pos',
                   ...,]
                 ]
                ]

        Examples
        --------
         ::

            bfx_client.liquidation_feed(start="1580020000000",end="1580058375000");
            bfx_client.liquidation_feed()

        """


        path = f"v2/liquidations/hist"
        params="?"
        for key, value in kwargs.items():
            params = f"{params}{key}={value}&"

        path = path + params[:-1]
        response = self._get(path)
        return response

    def leaderboards(self, key, timeframe, symbol, section="hist", **kwargs):
        """`Bitfinex Liquidation Feed reference
        <https://docs.bitfinex.com/reference#rest-public-rankings>`_

        The leaderboards endpoint allows you to retrieve leaderboard standings for unrealized
        profit (period delta), unrealized profit (inception), volume, and realized profit.

        Parameters
        ----------
        key : str 
            Allowed values: "plu_diff" for unrealized profit (period delta); "plu" for unrealized 
            profit (inception); "vol" for volume; "plr" for realized profit

        timeframe : str
            Available values: "3h", "1w", "1M" - see bitfinex documentation for available time frames per key

        symbol : str
            The symbol you want information about. (e.g. tBTCUSD, tETHUSD, tGLOBAL:USD)
             see bitfinex documentation for available symbols per key

        section : str
            available values : hist

        start : Optional int
            Millisecond start time

        end : Optional int
            Millisecond end time

        limit : Optional int
            Number of records (Max: 10000)

        sort : Optional int
            if = 1 it sorts results returned with old > new

        Returns
        -------
        list
             ::

                [[ 
                  MTS,
                  PLACEHOLDER,
                  USERNAME,
                  RANKING,
                  PLACEHOLDER,
                  PLACEHOLDER,
                  VALUE,
                  PLACEHOLDER
                  PLACEHOLDER
                  TWITTER_HANDLE
                ],
                 [
                  ...
                 ]
                ]

        Examples
        --------
         ::

            bfx_client.liquidation_feed(start="1580020000000",end="1580058375000");
            bfx_client.liquidation_feed()

        """

        path = f"v2/rankings/{key}:{timeframe}:{symbol}/{section}"
        params="?"
        for key, value in kwargs.items():
            params = f"{params}{key}={value}&"

        path = path + params[:-1]
        response = self._get(path)
        return response

    # REST CALCULATION ENDPOINTS
    def market_average_price(self, **kwargs):
        """`Bitfinex market average price reference
        <https://docs.bitfinex.com/reference#rest-public-calc-market-average-price>`_

        Calculate the average execution rate for Trading or Margin funding.

        Parameters
        ----------
        symbol : str
            The `symbol <restv1.html#symbols>`_ you want information about.

        amount : str
            Amount. Positive for buy, negative for sell (ex. "1.123")

        period : Optional int
            Maximum period for Margin Funding

        rate_limit : str
            Limit rate/price (ex. "1000.5")

        Returns
        -------
        list
             ::

                [RATE_AVG, AMOUNT]

        Example
        -------
         ::

            bfx_client.market_average_price(symbol="tBTCUSD", amount="100", period="1m")

        """

        path = f"v2/calc/trade/avg"
        params="?"
        for key, value in kwargs.items():
            params = f"{params}{key}={value}&"
        path = path + params[:-1]
        response = self._public_post(path,payload={}, verify=True)
        return response

    def foreign_exchange_rate(self, **kwargs):
        """`Bitfinex foreign exchange rate reference
        <https://docs.bitfinex.com/reference#rest-public-calc-foreign-exchange-rate>`_


        Parameters
        ----------
        ccy1 : str
            First currency

        ccy2 : str
            Second currency

        Returns
        -------
        list
             ::

                [ CURRENT_RATE ]

        Example
        -------
         ::

            bfx_client.foreign_exchange_rate(ccy1="IOT", ccy2="USD")

        """
        path = "v2/calc/fx"
        params="?"
        for key, value in kwargs.items():
            params = f"{params}{key}={value}&"
        path = path + params[:-1]

        response = self._public_post(path, payload={}, verify=True)
        return response

    # REST AUTHENTICATED ENDPOINTS
    def wallets_balance(self):
        """`Bitfinex wallets balance reference
        <https://docs.bitfinex.com/reference#rest-auth-wallets>`_

        Get account wallets

        Returns
        -------
        list
             ::

                [
                  [
                    WALLET_TYPE,
                    CURRENCY,
                    BALANCE,
                    UNSETTLED_INTEREST,
                    BALANCE_AVAILABLE,
                    ...
                  ],
                  ...
                ]

        Example
        -------
         ::

            bfx_client.wallets_balance()

        """

        body = {}
        raw_body = json.dumps(body)
        path = "v2/auth/r/wallets"
        response = self._post(path, raw_body, verify=True)
        return response

    def wallets_history(self, **kwargs):
        """`Get account wallet balances for a specific point in time using the "end" param.
        <https://docs.bitfinex.com/reference#rest-auth-wallets-hist>`_

        Get account wallets historic balance

        Returns
        -------
        list
             ::

                [
                  [
                    WALLET_TYPE, 
                    CURRENCY, 
                    BALANCE, 
                    UNSETTLED_INTEREST,
                    BALANCE_AVAILABLE,
                    PLACEHOLDER,
                    MTS_UPDATE
                  ], 
                  ...
                ]

                [["margin","BTC",0.00111839,0,null,null,1521244800000],["margin","USD",0.02024216,0,null,null,1544054400000],["funding","ETH",0.15158373,0,null,null,1527379200000]]  

        Example
        -------
         ::

            bfx_client.wallets_balance()

        """

        raw_body = json.dumps(kwargs)
        path = "v2/auth/r/wallets/hist"
        response = self._post(path, raw_body, verify=True)
        return response

    def active_orders(self, trade_pair=""):
        """`Bitfinex active orders reference
        <https://docs.bitfinex.com/reference#rest-auth-orders>`_

        Fetch active orders using rest api v2

        Parameters
        ----------
        symbol : Optional str
            The `symbol <restv1.html#symbols>`_ you want information about.

        Returns
        -------
        list
             ::

                [
                  [
                    ID,
                    GID,
                    CID,
                    SYMBOL,
                    MTS_CREATE,
                    MTS_UPDATE,
                    AMOUNT,
                    AMOUNT_ORIG,
                    TYPE,
                    TYPE_PREV,
                    _PLACEHOLDER,
                    _PLACEHOLDER,
                    FLAGS,
                    STATUS,
                    _PLACEHOLDER,
                    _PLACEHOLDER,
                    PRICE,
                    PRICE_AVG,
                    PRICE_TRAILING,
                    PRICE_AUX_LIMIT,
                    _PLACEHOLDER,
                    _PLACEHOLDER,
                    _PLACEHOLDER,
                    HIDDEN,
                    PLACED_ID,
                    ...
                  ],
                  ...
                ]

        Examples
        --------
         ::

            bfx_client.active_orders("tIOTUSD")
            bfx_client.active_orders()

        """

        path = "v2/auth/r/orders/{}".format(trade_pair)
        response = self._post(path, "", verify=True)
        return response

    def submit_order(self, order_type, symbol, price, amount, **kwargs):
        """`Bitfinex submit order reference
        <https://docs.bitfinex.com/reference#rest-auth-submit-order>`_

        Submit an Order.

        Parameters
        ----------
        order_type : str
            The type of the order: LIMIT, MARKET, STOP, STOP LIMIT, TRAILING STOP,
            EXCHANGE MARKET, EXCHANGE LIMIT, EXCHANGE STOP, EXCHANGE STOP LIMIT,
            EXCHANGE TRAILING STOP, FOK, EXCHANGE FOK, IOC, EXCHANGE IOC.

        symbol : str
            Symbol for desired pair (ex : 'tBTCUSD')

        price : str
            Price of order

        amount : str
            Amount of order (positive for buy, negative for sell)

        gid : Optional int32
            (optional) Group id for the order

        cid : Optional int32
            Client id, Should be unique in the day (UTC) (not enforced)

        flags : Optional int32
            `flags <https://docs.bitfinex.com/v2/docs/flag-values>`_

        lev : int32
            Set the leverage for a derivative order, supported by derivative symbol orders only.
            The value should be between 1 and 100 inclusive. The field is optional, 
            if omitted the default leverage value of 10 will be used.

        price_trailing : str
            The trailing price for a trailing stop order

        price_aux_limit : str
            Auxiliary Limit price (for STOP LIMIT)

        price_oco_stop : str
            One cancels other stop price

        tif : str
            Time-In-Force: datetime for automatic order cancellation (ie. 2020-01-01 10:45:23) )

        meta : The meta object allows you to pass along an affiliate code inside the object
               - example: meta: {aff_code: "AFF_CODE_HERE"}

        Returns
        -------
        list
             ::

                [
                  MTS, 
                  TYPE, 
                  MESSAGE_ID, 
                  null,

                  [[
                     ID,
                     GID,
                     CID,
                     SYMBOL,
                     MTS_CREATE, 
                     MTS_UPDATE, 
                     AMOUNT, 
                     AMOUNT_ORIG, 
                     TYPE,
                     TYPE_PREV,
                     MTS_TIF,
                     _PLACEHOLDER,
                     FLAGS,
                     ORDER_STATUS,
                     _PLACEHOLDER,
                     _PLACEHOLDER,
                     PRICE,
                     PRICE_AVG,
                     PRICE_TRAILING,
                     PRICE_AUX_LIMIT,
                     _PLACEHOLDER,
                     _PLACEHOLDER,
                     _PLACEHOLDER,
                     HIDDEN, 
                     PLACED_ID,
                     _PLACEHOLDER,
                     _PLACEHOLDER,
                     _PLACEHOLDER,
                     ROUTING,
                     _PLACEHOLDER,
                     _PLACEHOLDER,
                     META
                   ],
                   ]

                  CODE, 
                  STATUS, 
                  TEXT
                ]

                [1567590617.442,"on-req",null,null,[[30630788061,null,1567590617439,"tBTCUSD",
                1567590617439,1567590617439,0.001,0.001,"LIMIT",null,null,null,0,"ACTIVE",
                null,null,15,0,0,0,null,null,null,0,null,null,null,null,"API>BFX",null,null,null]],
                null,"SUCCESS","Submitting 1 orders."]

        Examples
        --------
         ::

            Submit order to sell 100 leo at 2$
            bfx_client.submit_order("EXCHANGE LIMIT", "tLEOUSD", "2.0", "-100");
            Submit order to sell 100 leo at 2$ with client id 1829 and make the order hidden
            bfx_client.submit_order("EXCHANGE LIMIT", "tLEOUSD", "2.0", "-100", cid=1729, flags=64);

        """
        body = {
            "type": order_type,
            "symbol": symbol,
            "price": str(price),
            "amount": str(amount),
            "meta": {"aff_code": "b2UR2iQr"},
            **kwargs
        }

        path = "v2/auth/w/order/submit"
        response = self._post(path, json.dumps(body), verify=True)
        return response

    def order_update(self, order_id, **kwargs):
        """`Bitfinex order update reference
        <https://docs.bitfinex.com/reference#rest-auth-order-update>`_

        Update an existing order, can be used to update margin, exchange, and derivative orders.

        Parameters
        ----------
        order_id : int32
            Order ID (Can be retrieved by calling the Retrieve Orders endpoint)

        cid : Optional int32
            Client id, Should be unique in the day (UTC) (not enforced)

        cid_date: 
            Client Order ID Date format must be YYYY-MM-DD

        gid : Optional int32
            (optional) Group id for the order

        amount : str
            Amount of order (positive for buy, negative for sell)

        price : str
            Price of order

        flags : Optional int32
            `flags <https://docs.bitfinex.com/v2/docs/flag-values>`_

        lev : int32
            Set the leverage for a derivative order, supported by derivative symbol orders only.
            The value should be between 1 and 100 inclusive. The field is optional, 
            if omitted the default leverage value of 10 will be used.

        delta : string
            Change of amount

        price_aux_limit : str
            Auxiliary Limit price (for STOP LIMIT)

        price_trailing : str
            The trailing price for a trailing stop order

        tif : str
            Time-In-Force: datetime for automatic order cancellation (ie. 2020-01-01 10:45:23) )

        Returns
        -------
        list
             ::

                [
                  MTS, 
                  TYPE, 
                  MESSAGE_ID, 
                  null,

                   [
                     ID,
                     GID,
                     CID,
                     SYMBOL,
                     MTS_CREATE, 
                     MTS_UPDATE, 
                     AMOUNT, 
                     AMOUNT_ORIG, 
                     TYPE,
                     TYPE_PREV,
                     MTS_TIF,
                     _PLACEHOLDER,
                     FLAGS,
                     ORDER_STATUS,
                     _PLACEHOLDER,
                     _PLACEHOLDER,
                     PRICE,
                     PRICE_AVG,
                     PRICE_TRAILING,
                     PRICE_AUX_LIMIT,
                     _PLACEHOLDER,
                     _PLACEHOLDER,
                     _PLACEHOLDER,
                     HIDDEN, 
                     PLACED_ID,
                     _PLACEHOLDER,
                     _PLACEHOLDER,
                     _PLACEHOLDER,
                     ROUTING,
                     _PLACEHOLDER,
                     _PLACEHOLDER,
                     META
                   ],

                  CODE, 
                  STATUS, 
                  TEXT
                ]

                [1568110298859,"ou-req",null,null,[30854813589,null,1568109670135,"tBTCUSD",
                1568109673000,1568109866000,0.002,0.002,"LIMIT","LIMIT",null,null,0,"ACTIVE",
                null,null,20,0,0,0,null,null,null,0,0,null,null,null,"API>BFX",null,null,null],
                null,"SUCCESS","Submitting update to limit buy order for 0.002 BTC."]

        Examples
        --------
         ::

            [38646826900, None, 1580627473757, 'tLEOUSD', 1580627474000,
            1580627474000, -100, -100, 'EXCHANGE LIMIT', None, None, None, 0,
            'ACTIVE', None, None, 2, 0, 0, 0, None, None, None, 0, 0, None,
            None, None, 'BFX', None, None, None], [38648166834, None, 1580629128587,
            'tLEOUSD', 1580629129000, 1580629129000, -100, -100, 'EXCHANGE LIMIT',
            None, None, None, 0, 'ACTIVE', None, None, 2, 0, 0, 0, None, None, None,
            0, 0, None, None, None, 'API>BFX', None, None, {'aff_code': 'b2UR2iQr'}]

            bfx_client.order_update(38646826900, price="2.01")
            bfx_client.order_update(38646826900, amount="-99")
            bfx_client.order_update(38646826900, price="2.02", amount="-98", flags=64)

        """
        body = {
            "id": order_id,
            **kwargs
        }

        path = "v2/auth/w/order/update"
        response = self._post(path, json.dumps(body), verify=True)
        return response

    def cancel_order(self, **kwargs):
        """`Bitfinex cancel order reference
        <https://docs.bitfinex.com/reference#rest-auth-cancel-order>`_

        Cancel an existing order, can be used to cancel margin, exchange, and derivative orders.
        You can cancel the order by the Internal Order ID or using a Client Order ID (supplied by you).
        The Client Order ID is unique per day, so you also have to provide the date of the order as a 
        date string in this format YYYY-MM-DD.

        Parameters
        ----------
        order_id : int32
            Order ID (Can be retrieved by calling the Retrieve Orders endpoint)

        cid : int32
            Client id, Should be unique in the day (UTC) (not enforced)

        cid_date: 
            Client Order ID Date format must be YYYY-MM-DD

        Returns
        -------
        list
             ::

                [
                  MTS, 
                  TYPE, 
                  MESSAGE_ID, 
                  null,

                  [
                     ID,
                     GID,
                     CID,
                     SYMBOL,
                     MTS_CREATE, 
                     MTS_UPDATE, 
                     AMOUNT, 
                     AMOUNT_ORIG, 
                     TYPE,
                     TYPE_PREV,
                     MTS_TIF,
                     _PLACEHOLDER,
                     FLAGS,
                     ORDER_STATUS,
                     _PLACEHOLDER,
                     _PLACEHOLDER,
                     PRICE,
                     PRICE_AVG,
                     PRICE_TRAILING,
                     PRICE_AUX_LIMIT,
                     _PLACEHOLDER,
                     _PLACEHOLDER,
                     _PLACEHOLDER,
                     HIDDEN, 
                     PLACED_ID,
                     _PLACEHOLDER,
                     _PLACEHOLDER,
                     _PLACEHOLDER,
                     ROUTING,
                     _PLACEHOLDER,
                     _PLACEHOLDER,
                     META
                   ]

                  CODE, 
                  STATUS, 
                  TEXT
                ]

                [1568298355648,"oc-req",null,null,[30937950333,null,1568298279766,"tBTCUSD",
                1568298281000,1568298281000,0.001,0.001,"LIMIT",null,null,null,0,"ACTIVE",
                null,null,15,0,0,0,null,null,null,0,0,null,null,null,"API>BFX",null,null,
                null],null,"SUCCESS","Submitted for cancellation; waiting for confirmation
                (ID: 30937950333)."]
        Examples
        --------
         ::

            bfx_client.cancel_order(id=38646826900)
            bfx_client.cancel_order(cid=1729, date="2020-02-04")

            Canceling by clientid did not work at the time this was written 04/02/2020


        """
        body = {
            **kwargs
        }
        path = "v2/auth/w/order/cancel"
        response = self._post(path, json.dumps(body), verify=True)
        return response

    def get_order_op(self, op, **kwargs):
        """ utility method to create new order operation

        It supports the creation of operations for new order, update order, cancel order,
        multiple cancel order

        Parameters
        ----------
        op : Enum(Operation)
            Operation must be imported from utils

        kwargs : key value parameters for the operation you want created 

        Returns
        -------
        list
             ::

                [
                  OPERATION, 
                  {
                    ORDER_TYPE,
                    ID,
                    ...
                  }
                ]

                ['on', {'order_type': 'EXCHANGE_LIMIT', 'symbol': 'tLEOUSD', 'price': '3', 'amount': '10'}]
                ['ou', {'id': 124342, 'amount': '10'}]
                ['oc', {'id': 124342}]
                ['oc_multi', {'id': [124342, 32432]}]

        Examples
        --------
         ::

            from bitfinex import ClientV2 as Client2
            from bitfinex.utils import Operation as Op
            bfx_client = Client2('', '')
            bfx_client.get_order_op(
                Op.NEW,
                type="EXCHANGE_LIMIT",
                symbol="tLEOUSD",
                price="3",
                amount="10"
                )

            bfx_client.get_order_op(
                Op.UPDATE,
                id=124342,
                amount="10"
                )

            bfx_client.get_order_op(
                Op.CANCEL,
                id=124342
                )

            bfx_client.get_order_op(
                Op.MULTI_CANCEL,
                id=[124342, 32432]
                )


        """
        assert isinstance(op, utils.Operation), "Please use the Operation enum from utils"
        op_code = utils.OPERATION_CODE[op]

        if op == utils.Operation.NEW:
            assert "type" in kwargs
            assert "symbol" in kwargs
            assert "price" in kwargs
            assert "amount" in kwargs

        if op == utils.Operation.UPDATE:
            assert "id" in kwargs
            assert isinstance(kwargs["id"], int)
            assert len(kwargs.keys()) > 1

        if op == utils.Operation.CANCEL:
            assert "id" in kwargs
            assert isinstance(kwargs["id"], int)
            assert len(kwargs.keys()) == 1

        if op == utils.Operation.MULTI_CANCEL:
            assert "id" in kwargs
            assert isinstance(kwargs["id"], list)
            assert len(kwargs.keys()) == 1

        order_op = [
            utils.OPERATION_CODE[op],
            { **kwargs }
        ]

        return order_op

    def order_multi_op(self, order_ops):
        """`Bitfinex order multi reference
        <https://docs.bitfinex.com/reference#rest-auth-order-multi>`_

        Send Multiple order-related operations. Please note the sent object has only one property
        with a value of an array of arrays detailing each order operation.

        Parameters
        ----------
        order_type : str
            The type of the order: LIMIT, MARKET, STOP, STOP LIMIT, TRAILING STOP,
            EXCHANGE MARKET, EXCHANGE LIMIT, EXCHANGE STOP, EXCHANGE STOP LIMIT,
            EXCHANGE TRAILING STOP, FOK, EXCHANGE FOK, IOC, EXCHANGE IOC.

        symbol : str
            Symbol for desired pair (ex : 'tBTCUSD')

        price : str
            Price of order

        amount : str
            Amount of order (positive for buy, negative for sell)

        gid : Optional int32
            (optional) Group id for the order

        cid : Optional int32
            Client id, Should be unique in the day (UTC) (not enforced)

        flags : Optional int32
            `flags <https://docs.bitfinex.com/v2/docs/flag-values>`_

        lev : int32
            Set the leverage for a derivative order, supported by derivative symbol orders only.
            The value should be between 1 and 100 inclusive. The field is optional, 
            if omitted the default leverage value of 10 will be used.

        price_trailing : str
            The trailing price for a trailing stop order

        price_aux_limit : str
            Auxiliary Limit price (for STOP LIMIT)

        price_oco_stop : str
            One cancels other stop price

        tif : str
            Time-In-Force: datetime for automatic order cancellation (ie. 2020-01-01 10:45:23) )

        cid_date: str
            Client Order Id Data

        all: int
            Cancel all open orders if value is set to: 1

        Returns
        -------
        list
        ::

            [
              MTS, 
              TYPE, 
              MESSAGE_ID, 
              null,

              [
                 ID,
                 GID,
                 CID,
                 SYMBOL,
                 MTS_CREATE, 
                 MTS_UPDATE, 
                 AMOUNT, 
                 AMOUNT_ORIG, 
                 TYPE,
                 TYPE_PREV,
                 MTS_TIF,
                 _PLACEHOLDER,
                 FLAGS,
                 ORDER_STATUS,
                 _PLACEHOLDER,
                 _PLACEHOLDER,
                 PRICE,
                 PRICE_AVG,
                 PRICE_TRAILING,
                 PRICE_AUX_LIMIT,
                 _PLACEHOLDER,
                 _PLACEHOLDER,
                 _PLACEHOLDER,
                 HIDDEN, 
                 PLACED_ID,
                 _PLACEHOLDER,
                 _PLACEHOLDER,
                 _PLACEHOLDER,
                 ROUTING,
                 _PLACEHOLDER,
                 _PLACEHOLDER,
                 META
               ]

              CODE, 
              STATUS, 
              TEXT
            ]

            [1568298355648,"oc-req",null,null,[30937950333,null,1568298279766,"tBTCUSD",
            1568298281000,1568298281000,0.001,0.001,"LIMIT",null,null,null,0,"ACTIVE",
            null,null,15,0,0,0,null,null,null,0,0,null,null,null,"API>BFX",null,null,null],
            null,"SUCCESS","Submitted for cancellation;
            waiting for confirmation (ID: 30937950333)."]

        Examples
        --------
         ::

            order_op = bfx_client.get_order_op(
                Op.MULTI_CANCEL,
                id=[38646826900, 38648166834]
            )

            ops = [order_op]
            order_op = bfx_client.get_order_op(
                Op.NEW,
                type="EXCHANGE LIMIT",
                symbol="tLEOUSD",
                price="3",
                amount="-10"
            )
            ops.append(order_op)

            resp = bfx_client.order_multi_op(ops)
            print(resp)

        """
        body = {
            "ops" : order_ops
        }

        path = "v2/auth/w/order/multi"
        response = self._post(path, json.dumps(body), verify=True)
        return response

    def cancel_order_multi(self, **kwargs):
        """`Bitfinex cancel order multi reference
        <https://docs.bitfinex.com/reference#rest-auth-order-cancel-multi>`_

        Cancel multiple orders simultaneously.

        Orders can be canceled based on the Order ID, the combination of Client Order ID
        and Client Order Date, or the Group Order ID. Alternatively, the body param 'all'
        can be used with a value of 1 to cancel all orders.

        Parameters
        ----------
        id : list
            Order ID (Can be retrieved by calling the Retrieve Orders endpoint)

        cid : int32
            Client id, Should be unique in the day (UTC) (not enforced)

        cid_date: str
            Client Order ID Date format must be YYYY-MM-DD

        gid: int
            Group Order ID

        all: int
            Cancel all open orders if value is set to: 1 (Trading and Derivatives)

        Returns
        -------
        list
             ::

                [[
                    ID,
                    GID,
                    CID,
                    SYMBOL,
                    MTS_CREATE, 
                    MTS_UPDATE, 
                    AMOUNT, 
                    AMOUNT_ORIG, 
                    TYPE,
                    TYPE_PREV,
                    MTS_TIF,
                    _PLACEHOLDER,
                    FLAGS,
                    ORDER_STATUS,
                    _PLACEHOLDER,
                    _PLACEHOLDER,
                    PRICE,
                    PRICE_AVG,
                    PRICE_TRAILING,
                    PRICE_AUX_LIMIT,
                    _PLACEHOLDER,
                    _PLACEHOLDER,
                    _PLACEHOLDER,
                    _PLACEHOLDER,
                    HIDDEN, 
                    PLACED_ID,
                    _PLACEHOLDER,
                    _PLACEHOLDER,
                    ROUTING,
                    _PLACEHOLDER,
                    _PLACEHOLDER,
                    META
                   ],
                    [ID, ...]
                   ],
                  CODE, 
                  STATUS, 
                  TEXT
                ]
    
                [1568711312683,"oc_multi-req",null,null,[[31123704044,null,1568711144715,"tBTCUSD",
                1568711147000,1568711147000,0.001,0.001,"LIMIT",null,null,null,0,"ACTIVE",null,
                null,15,0,0,0,null,null,null,0,0,null,null,null,"API>BFX",null,null,null],
                [31123725368,null,1568711155664,"tBTCUSD",1568711158000,1568711158000,0.001,0.001,
                "LIMIT",null,null,null,0,"ACTIVE",null,null,15,0,0,0,null,null,null,0,0,null,null,
                null,"API>BFX",null,null,null]],null,"SUCCESS","Submitting 2 order cancellations."]
        Examples
        --------
         ::

            bfx_client.cancel_order_multi(id=[39259104169, 39271246477])
            bfx_client.cancel_order_multi(cid=[[1729, "2020-02-10"], [1729, "2020-02-02"]])
            bfx_client.cancel_order_multi(all=1)
            Canceling using cid did not work at the time this was written 11/02/2020


        """
        body = {
            **kwargs
        }
        path = "v2/auth/w/order/cancel/multi"
        response = self._post(path, json.dumps(body), verify=True)
        return response

    def orders_history(self, trade_pair=None, **kwargs):
        """`Bitfinex orders history reference
        <https://docs.bitfinex.com/reference#rest-auth-orders-history>`_

        Returns the most recent closed or canceled orders up to circa two weeks ago

        Parameters
        ----------
        symbol : str
            The `symbol <restv1.html#symbols>`_ you want information about.

        start : Optional int
            Millisecond start time

        end : Optional int
            Millisecond end time

        limit : Optional int
            Number of records

        id : Optional list 
            Allows you to retrieve specific orders by order ID (id: [ID1, ID2, ID3])

        Returns
        -------
        list
             ::

                [
                  [
                    ID,
                    GID,
                    CID,
                    SYMBOL,
                    MTS_CREATE, 
                    MTS_UPDATE, 
                    AMOUNT, 
                    AMOUNT_ORIG, 
                    TYPE,
                    TYPE_PREV,
                    MTS_TIF,
                    _PLACEHOLDER,
                    FLAGS,
                    ORDER_STATUS,
                    _PLACEHOLDER,
                    _PLACEHOLDER,
                    PRICE,
                    PRICE_AVG,
                    PRICE_TRAILING,
                    PRICE_AUX_LIMIT,
                    _PLACEHOLDER,
                    _PLACEHOLDER,
                    _PLACEHOLDER,
                    _PLACEHOLDER,
                    HIDDEN, 
                    PLACED_ID,
                    _PLACEHOLDER,
                    _PLACEHOLDER,
                    ROUTING,
                    _PLACEHOLDER,
                    _PLACEHOLDER,
                    META
                  ],
                  ...
                ]

                [[33961681942,"1227",1337,"tBTCUSD",1573482478000,1573485373000,0.001,0.001,
                "EXCHANGE LIMIT",null,null,null,"0","CANCELED",null,null,15,0,0,0,null,null,null,
                0,0,null,null,null,"API>BFX",null,null,null],[33950998276,null,1573476812756,
                "tBTCUSD",1573476813000,1573485371000,0.0026,0.0026,"LIMIT",null,null,null,"0",
                "CANCELED",null,null,8000,0,0,0,null,null,null,0,0,null,null,null,"BFX",
                null,null,null]]

        Example
        -------
         ::

            bfx_client.orders_history("tIOTUSD")
            bfx_client.orders_history(id=[29889265065,29865773141])

        """

        body = kwargs
        raw_body = json.dumps(body)
        if trade_pair:
            path = "v2/auth/r/orders/{}/hist".format(trade_pair)
        else:
            path = "v2/auth/r/orders/hist"
        response = self._post(path, raw_body, verify=True)
        return response

    def order_trades(self, trade_pair, order_id):
        """`Bitfinex order trades reference
        <https://docs.bitfinex.com/reference#rest-auth-order-trades>`_

        Get Trades generated by an Order

        Parameters
        ----------
        symbol : str
            The `symbol <restv1.html#symbols>`_ you want information about.

        orderid : int
            Order id

        Returns
        -------
        list
             ::

                [
                  [
                    ID,
                    PAIR,
                    MTS_CREATE,
                    ORDER_ID,
                    EXEC_AMOUNT,
                    EXEC_PRICE,
                    _PLACEHOLDER,
                    _PLACEHOLDER,
                    MAKER,
                    FEE,
                    FEE_CURRENCY,
                    ...
                  ],
                  ...
                ]

        Example
        -------
         ::

            bfx_client.order_trades("tIOTUSD", 14395751815)

        """
        body = {}
        raw_body = json.dumps(body)
        path = "v2/auth/r/order/{}:{}/trades".format(trade_pair, order_id)
        response = self._post(path, raw_body, verify=True)
        return response

    def trades_history(self, trade_pair=None, **kwargs):
        """`Bitfinex trades history reference
        <https://docs.bitfinex.com/reference#rest-auth-trades-hist>`_

        List of trades

        Parameters
        ----------
        trade_pair : Optional str
            The `symbol <restv1.html#symbols>`_ you want information about.
            Omit for all symbols

        start : Optional int
            Millisecond start time

        end : Optional int
            Millisecond end time

        limit : Optional int
            Number of records

        sort : Optional int
            set to 1 to get results in ascending order


        Returns
        -------
        list
             ::

                [
                  [
                    ID,
                    PAIR,
                    MTS_CREATE,
                    ORDER_ID,
                    EXEC_AMOUNT,
                    EXEC_PRICE,
                    ORDER_TYPE,
                    ORDER_PRICE,
                    MAKER,
                    FEE,
                    FEE_CURRENCY,
                    ...
                  ],
                  ...
                ]

        Examples
        --------
         ::

            bfx_client.trades_history('tIOTUSD', limit=10)

            TH = BTFXCLIENT.trades_history("tIOTUSD")
            for trade in TH:
                print(trade)

        """

        raw_body = json.dumps(kwargs)
        if trade_pair is None:
            path = "v2/auth/r/trades/hist"  # will load history for all pairs
        else:
            path = "v2/auth/r/trades/{}/hist".format(trade_pair)
        response = self._post(path, raw_body, verify=True)
        return response

    def ledgers(self, currency="",  **kwargs):
        """`Bitfinex ledgers reference
        <https://docs.bitfinex.com/reference#rest-auth-ledgers>`_

        View your past ledger entries.

        Parameters
        ----------
        Currency : str
            Currency (BTC, ...)

        start : Optional int
            Millisecond start time

        end : Optional int
            Millisecond end time

        limit : Optional int
            Number of records

        Returns
        -------
        list
             ::

            [
              [
                ID,
                CURRENCY,
                MTS,
                AMOUNT,
                BALANCE,
                DESCRIPTION
              ],
              ...
            ]

        Example
        --------
         ::

            bfx_client.ledgers('IOT')

        """
        raw_body = json.dumps(kwargs)
        add_currency = "{}/".format(currency.upper()) if currency else ""
        path = "v2/auth/r/ledgers/{}hist".format(add_currency)
        response = self._post(path, raw_body, verify=True)
        return response

    def margin_info(self, tradepair="base"):
        """`Bitfinex margin info reference
        <https://docs.bitfinex.com/reference#rest-auth-info-margin>`_

        Get account margin info

        Parameters
        ----------
        key : str
            "base" | SYMBOL

        Returns
        -------
        list
             ::

                # margin base
                [
                  "base",
                  [
                    USER_PL,
                    USER_SWAPS,
                    MARGIN_BALANCE,
                    MARGIN_NET,
                    ...
                  ]
                ]

                # margin symbol
                [
                  SYMBOL,
                  [
                    TRADABLE_BALANCE,
                    GROSS_BALANCE,
                    BUY,
                    SELL,
                    ...
                  ]
                ]

        Examples
        --------
         ::

            bfx_client.margin_info()

            bfx_client.margin_info('base')

            bfx_client.margin_info('tIOTUSD')

        """
        body = {}
        raw_body = json.dumps(body)
        path = "v2/auth/r/info/margin/{}".format(tradepair)
        response = self._post(path, raw_body, verify=True)
        return response

    def active_positions(self):
        """`Bitfinex positions reference
        <https://docs.bitfinex.com/reference#rest-auth-positions>`_

        Get active positions

        Returns
        -------
        list
             ::

                [
                  [
                    SYMBOL,
                    STATUS,
                    AMOUNT,
                    BASE_PRICE,
                    MARGIN_FUNDING,
                    MARGIN_FUNDING_TYPE,
                    PL,
                    PL_PERC,
                    PRICE_LIQ,
                    LEVERAGE
                    ...
                  ],
                  ...
                ]

        Example
        -------
         ::

            bfx_client.active_positions()

        """
        body = {}
        raw_body = json.dumps(body)
        path = "v2/auth/r/positions"
        response = self._post(path, raw_body, verify=True)
        return response

    def claim_position(self):
        raise NotImplementedError

    def positions_history(self, **kwargs):
        """`Bitfinex positions history reference
        <https://docs.bitfinex.com/reference#rest-auth-positions-hist>`_

        Return the positions of a user between two dates

        Parameters
        ----------
        start : Optional int
            Millisecond start time

        end : Optional int
            Millisecond end time

        limit : Optional int
            Number of records

        Returns
        -------
        list
             ::

                [
                  [
                    SYMBOL,
                    STATUS,
                    AMOUNT,
                    BASE_PRICE,
                    MARGIN_FUNDING,
                    MARGIN_FUNDING_TYPE,
                    PL,
                    PL_PERC,
                    PRICE_LIQ,
                    LEVERAGE,
                    ID,
                    MTS_CREATE,
                    MTS_UPDATE
                  ],
                  ...
                ]

        Examples
        --------
         ::

            positions = bfx_client.positions_history(limit=10)
            for position in positions:
                print(position)

        """

        body = kwargs
        raw_body = json.dumps(body)
        path = "v2/auth/r/positions/hist"
        response = self._post(path, raw_body, verify=True)
        return response

    def positions_audit(self, **kwargs):
        """`Bitfinex positions audit reference
        <https://docs.bitfinex.com/reference#rest-auth-positions-audit>`_

        Return and audit of the positions of a user that correspond to the ids send

        Parameters
        ----------
        id : Optional list of ints
            List of position IDs to audit

        start : Optional int
            Millisecond start time

        end : Optional int
            Millisecond end time

        limit : Optional int
            Number of records

        Returns
        -------
        list
             ::

                [
                  [
                    SYMBOL,
                    STATUS,
                    AMOUNT,
                    BASE_PRICE,
                    MARGIN_FUNDING,
                    MARGIN_FUNDING_TYPE,
                    PL,
                    PL_PERC,
                    PRICE_LIQ,
                    LEVERAGE,
                    ID,
                    MTS_CREATE,
                    MTS_UPDATE,
                    TYPE,
                    COLLATERAL,
                    COLLATERAL_MIN,
                    META
                  ],
                  ...
                ]

        Examples
        --------
         ::

            positions = bfx_client.positions_audit([1, 2, 3])
            for position in positions:
                print(position)

        """

        body = kwargs
        raw_body = json.dumps(body)
        path = "v2/auth/r/positions/audit"
        response = self._post(path, raw_body, verify=True)
        return response

    def derivative_position_collateral(self):
        raise NotImplementedError

    def funding_offers(self, symbol=""):
        """`Bitfinex funding offers reference
        <https://docs.bitfinex.com/reference#rest-auth-funding-offers>`_

        Get active funding offers.

        Parameters
        ----------
        symbol : str
            The `symbol <restv1.html#symbols>`_ you want information about.

        Returns
        -------
        list
             ::

                [
                  [
                    ID,
                    SYMBOL,
                    MTS_CREATED,
                    MTS_UPDATED,
                    AMOUNT,
                    AMOUNT_ORIG,
                    TYPE,
                    _PLACEHOLDER,
                    _PLACEHOLDER,
                    FLAGS,
                    STATUS,
                    _PLACEHOLDER,
                    _PLACEHOLDER,
                    _PLACEHOLDER,
                    RATE,
                    PERIOD,
                    NOTIFY,
                    HIDDEN,
                    _PLACEHOLDER,
                    RENEW,
                    ...
                  ],
                  ...
                ]

        Examples
        --------
         ::

            bfx_client.funding_offers()

            bfx_client.funding_offers("fIOT")

        """
        body = {}
        raw_body = json.dumps(body)
        path = "v2/auth/r/funding/offers/{}".format(symbol)
        response = self._post(path, raw_body, verify=True)
        return response

    def submit_funding_offer(self):
        raise NotImplementedError

    def cancel_funding_offer(self):
        raise NotImplementedError

    def cancel_all_funding_offers(self):
        raise NotImplementedError

    def funding_close(self):
        raise NotImplementedError

    def funding_auto_renew(self):
        raise NotImplementedError

    def keep_funding(self):
        raise NotImplementedError

    def funding_offers_history(self, symbol="", **kwargs):
        """`Bitfinex funding offers hist reference
        <https://docs.bitfinex.com/reference#rest-auth-funding-offers-hist>`_

        Get past inactive funding offers. Limited to last 3 days.

        Parameters
        ----------
        symbol : str
            The `symbol <restv1.html#symbols>`_ you want information about.

        start : Optional int
            Millisecond start time

        end : Optional int
            Millisecond end time

        limit : Optional int
            Number of records

        Returns
        -------
        list
             ::

                [
                  [
                    ID,
                    SYMBOL,
                    MTS_CREATED,
                    MTS_UPDATED,
                    AMOUNT,
                    AMOUNT_ORIG,
                    TYPE,
                    _PLACEHOLDER,
                    _PLACEHOLDER,
                    FLAGS,
                    STATUS,
                    _PLACEHOLDER,
                    _PLACEHOLDER,
                    _PLACEHOLDER,
                    RATE,
                    PERIOD,
                    NOTIFY,
                    HIDDEN,
                    _PLACEHOLDER,
                    RENEW,
                    ...
                  ],
                  ...
                ]

        Examples
        --------
         ::

            bfx_client.funding_offers_history()

            bfx_client.funding_offers_history('fOMG')

        """
        body = kwargs
        raw_body = json.dumps(body)
        add_symbol = "{}/".format(symbol) if symbol else ""
        path = "v2/auth/r/funding/offers/{}hist".format(add_symbol)
        response = self._post(path, raw_body, verify=True)
        return response

    def funding_loans(self, symbol=""):
        """`Bitfinex funding loans reference
        <https://docs.bitfinex.com/reference#rest-auth-funding-loans>`_

        Funds not used in active positions

        Parameters
        ----------
        symbol : str
            The `symbol <restv1.html#symbols>`_ you want information about.

        Returns
        -------
        list
             ::

                [
                  [
                    ID,
                    SYMBOL,
                    SIDE,
                    MTS_CREATE,
                    MTS_UPDATE,
                    AMOUNT,
                    FLAGS,
                    STATUS,
                    _PLACEHOLDER,
                    _PLACEHOLDER,
                    _PLACEHOLDER,
                    RATE,
                    PERIOD,
                    MTS_OPENING,
                    MTS_LAST_PAYOUT,
                    NOTIFY,
                    HIDDEN,
                    _PLACEHOLDER,
                    RENEW,
                    _PLACEHOLDER,
                    NO_CLOSE,
                    ...
                  ],
                  ...
                ]

        Example
        -------
         ::

            bfx_client.funding_loans('fOMG')

        """
        body = {}
        raw_body = json.dumps(body)
        path = "v2/auth/r/funding/loans/{}".format(symbol)
        response = self._post(path, raw_body, verify=True)
        return response

    def funding_loans_history(self, symbol="", **kwargs):
        """`Bitfinex funding loans history reference
        <https://docs.bitfinex.com/reference#rest-auth-funding-loans-hist>`_

        Inactive funds not used in positions. Limited to last 3 days.

        Parameters
        ----------
        symbol : str
            The `symbol <restv1.html#symbols>`_ you want information about.

        start : Optional int
            Millisecond start time

        end : Optional int
            Millisecond end time

        limit : Optional int
            Number of records

        Returns
        -------
        list
             ::

                [
                  [
                    ID,
                    SYMBOL,
                    SIDE,
                    MTS_CREATE,
                    MTS_UPDATE,
                    AMOUNT,
                    FLAGS,
                    STATUS,
                    _PLACEHOLDER,
                    _PLACEHOLDER,
                    _PLACEHOLDER,
                    RATE,
                    PERIOD,
                    MTS_OPENING,
                    MTS_LAST_PAYOUT,
                    NOTIFY,
                    HIDDEN,
                    _PLACEHOLDER,
                    RENEW,
                    _PLACEHOLDER,
                    NO_CLOSE,
                    ...
                  ],
                  ...
                ]

        Example
        -------
         ::

            bfx_client.funding_loans_history('fOMG')

        """
        body = kwargs
        raw_body = json.dumps(body)
        add_symbol = "{}/".format(symbol) if symbol else ""
        path = "v2/auth/r/funding/loans/{}hist".format(add_symbol)
        response = self._post(path, raw_body, verify=True)
        return response

    def funding_credits(self, symbol=""):
        """`Bitfinex funding credits reference
        <https://docs.bitfinex.com/reference#rest-auth-funding-credits>`_

        Funds used in active positions

        Parameters
        ----------
        symbol : str
            The `symbol <restv1.html#symbols>`_ you want information about.

        Returns
        -------
        list
             ::

                [
                  [
                    ID,
                    SYMBOL,
                    SIDE,
                    MTS_CREATE,
                    MTS_UPDATE,
                    AMOUNT,
                    FLAGS,
                    STATUS,
                    _PLACEHOLDER,
                    _PLACEHOLDER,
                    _PLACEHOLDER,
                    RATE,
                    PERIOD,
                    MTS_OPENING,
                    MTS_LAST_PAYOUT,
                    NOTIFY,
                    HIDDEN,
                    _PLACEHOLDER,
                    RENEW,
                    _PLACEHOLDER,
                    NO_CLOSE,
                    ...
                  ],
                  ...
                ]

        Example
        -------
         ::

            bfx_client.funding_credits('fUSD')

        """
        body = {}
        raw_body = json.dumps(body)
        path = "v2/auth/r/funding/credits/{}".format(symbol)
        response = self._post(path, raw_body, verify=True)
        return response

    def funding_credits_history(self, symbol="", **kwargs):
        """`Bitfinex funding credits history reference
        <https://docs.bitfinex.com/reference#rest-auth-funding-credits-hist>`_

        Inactive funds used in positions. Limited to last 3 days.

        Parameters
        ----------
        symbol : str
            The `symbol <restv1.html#symbols>`_ you want information about.

        start : Optional int
            Millisecond start time

        end : Optional int
            Millisecond end time

        limit : Optional int
            Number of records

        Returns
        -------
        list
             ::

                [
                  [
                    ID,
                    SYMBOL,
                    SYMBOL,
                    MTS_CREATE,
                    MTS_UPDATE,
                    AMOUNT,
                    FLAGS,
                    STATUS,
                    _PLACEHOLDER,
                    _PLACEHOLDER,
                    _PLACEHOLDER,
                    RATE,
                    PERIOD,
                    MTS_OPENING,
                    MTS_LAST_PAYOUT,
                    NOTIFY,
                    HIDDEN,
                    _PLACEHOLDER,
                    RENEW,
                    _PLACEHOLDER,
                    NO_CLOSE,
                    POSITION_PAIR,
                    ...
                  ],
                  ...
                ]

        Example
        -------
         ::

            bfx_client.funding_credits_history('fUSD')

        """
        body = kwargs
        raw_body = json.dumps(body)
        add_symbol = "{}/".format(symbol) if symbol else ""
        path = "v2/auth/r/funding/credits/{}hist".format(add_symbol)
        response = self._post(path, raw_body, verify=True)
        return response

    def funding_trades(self, symbol="", **kwargs):
        """`Bitfinex funding trades hitory reference
        <https://docs.bitfinex.com/reference#rest-auth-funding-trades-hist>`_

        Get funding trades

        Parameters
        ----------
        symbol : str
            The `symbol <restv1.html#symbols>`_ you want information about.

        start : Optional int
            Millisecond start time

        end : Optional int
            Millisecond end time

        limit : Optional int
            Number of records

        Returns
        -------
        list
             ::

                [
                  [
                    ID,
                    CURRENCY,
                    MTS_CREATE,
                    OFFER_ID,
                    AMOUNT,
                    RATE,
                    PERIOD,
                    MAKER,
                    ...
                  ],
                  ...
                ]

        Example
        -------
         ::

            bfx_client.funding_trades('fUSD')

        """
        body = kwargs
        raw_body = json.dumps(body)
        add_symbol = "{}/".format(symbol) if symbol else ""
        path = "v2/auth/r/funding/trades/{}hist".format(add_symbol)
        response = self._post(path, raw_body, verify=True)
        return response

    def funding_info(self, tradepair):
        """`Bitfinex funding info reference
        <https://docs.bitfinex.com/reference#rest-auth-info-funding>`_

        Get account funding info

        Parameters
        ----------
        symbol : str
            The `symbol <restv1.html#symbols>`_ you want information about.

        Returns
        -------
        list
             ::

                [
                  "sym",
                  SYMBOL,
                  [
                    YIELD_LOAN,
                    YIELD_LEND,
                    DURATION_LOAN,
                    DURATION_LEND,
                    ...
                  ],
                  ...
                ]

        Example
        -------
         ::

            bfx_client.funding_info('fIOT')

        """
        body = {}
        raw_body = json.dumps(body)
        path = "v2/auth/r/info/funding/{}".format(tradepair)
        response = self._post(path, raw_body, verify=True)
        return response

    def user_info(self):
        raise NotImplementedError

    def transfer_between_wallets(self, from_wallet, to_wallet, **kwargs):
        """`Bitfinex Transfer funds between wallets.
        Can also be used to convert USDT to USDT0 for derivatives trading.
        <https://docs.bitfinex.com/reference#rest-auth-transfer`_

        Post transfer between wallets

        Parameters
        ----------
        from_wallet : str
            Select the wallet from which to transfer (exchange, margin, funding
            (can also use the old labels which are exchange, trading and deposit respectively))

        to_wallet: str
            Select the wallet from which to transfer (exchange, margin, funding
            (can also use the old labels which are exchange, trading and deposit respectively))

        currency: str
        Select the currency that you would like to transfer (USD, UST, BTC, ....)

        currency_to: str
            (optional) Select the currency that you would like to exchange to (USTF0 === USDT for derivatives pairs)

        amount: str
            Select the amount to transfer

        email_dst: str
            (optional) Allows transfer of funds to a sub- or master-account identified by the associated email address

        Returns
        -------
        list
             ::
                [
                  MTS,
                  TYPE,
                  MESSAGE_ID,
                  null,
                  [
                    MTS_UPDATE,
                    WALLET_FROM,
                    WALLET_TO,
                    _PLACEHOLDER,
                    CURRENCY,
                    CURRENCY_TO,
                    _PLACEHOLDER,
                    AMOUNT
                  ]
                  CODE,
                  STATUS,
                  TEXT
                ]

        //Transfer
        [1568736745789,"acc_tf",null,null,[1568736745790,"margin","exchange",null,"USD",null,null,50],null,
         "SUCCESS","50.0 US Dollar transferred from Margin to Exchange"]

        //Transfer and conversion to USDT0
        [1574173088379,"acc_tf",null,null,[1574173088379,"exchange","margin",null,"UST","USTF0",null,200],null,
        "SUCCESS","200.0 Tether USDt transfered from Exchange to Margin"]

        Example
        -------
         ::
            bfx_client.transfer_between_wallets(from_wallet='margin',
                                                to_wallet='exchange',
                                                currency='USTF0',
                                                currency_to='UST'
                                                amount='1.31')
        """
        body = {
            "from": from_wallet,
            "to": to_wallet,
            **kwargs
        }
        raw_body = json.dumps(body)
        path = "v2/auth/w/transfer"
        response = self._post(path, raw_body, verify=True)
        return response

    def deposit_address(self):
        raise NotImplementedError

    def withdrawal(self):
        raise NotImplementedError

    def movements(self, currency="", **kwargs):
        """`Bitfinex movements reference
        <https://docs.bitfinex.com/reference#rest-auth-movements>`_

        View your past deposits/withdrawals.

        Parameters
        ----------
        currency : str
            Currency (BTC, ...)

        start : Optional int
            Millisecond start time

        end : Optional int
            Millisecond end time

        limit : Optional int
            Number of records, default & max: 25

        Returns
        -------
        list
             ::

                [
                  [
                    ID,
                    CURRENCY,
                    CURRENCY_NAME,
                    null,
                    null,
                    MTS_STARTED,
                    MTS_UPDATED,
                    null,
                    null,
                    STATUS,
                    null,
                    null,
                    AMOUNT,
                    FEES,
                    null,
                    null,
                    DESTINATION_ADDRESS,
                    null,
                    null,
                    null,
                    TRANSACTION_ID,
                    null
                  ],
                  ...
                ]

        Example
        -------
         ::

            bfx_client.movements()

            bfx_client.movements("BTC")

        """
        body = kwargs
        raw_body = json.dumps(body)
        add_currency = "{}/".format(currency.upper()) if currency else ""
        path = "v2/auth/r/movements/{}hist".format(add_currency)
        response = self._post(path, raw_body, verify=True)
        return response

    def alert_list(self):
        """`Bitfinex list alerts reference
        <https://docs.bitfinex.com/reference#rest-auth-alerts>`_

        List of active alerts

        Returns
        -------
        list
             ::

                [
                  [
                    'price:tBTCUSD:560.92',
                    'price',
                    'tBTCUSD',
                    560.92,
                    91
                  ],
                  ...
                ]

        Example
        -------
         ::

            bfx_client.alert_list()

        """
        body = {'type': 'price'}
        raw_body = json.dumps(body)
        path = "v2/auth/r/alerts"
        response = self._post(path, raw_body, verify=True)
        return response

    def alert_set(self, alert_type, symbol, price):
        """`Bitfinex auth alert set reference
        <https://docs.bitfinex.com/reference#rest-auth-alert-set>`_

        Sets up a price alert at the given value

        Parameters
        ----------
        type : str
            Only one type is available : "price"

        symbol : str
            The `symbol <restv1.html#symbols>`_ you want information about.

        price : float
            Price where you want to receive alerts

        Returns
        -------
        list
             ::

                [
                  'price:tBTCUSD:600',
                  'price',
                  'tBTCUSD',
                  600,
                  100
                ]

        Example
        -------
         ::

            bfx_client.alert_set('price', 'tIOTUSD', 3)

        """
        body = {
            'type': alert_type,
            'symbol': symbol,
            'price': price
        }

        raw_body = json.dumps(body)
        path = "v2/auth/w/alert/set"
        response = self._post(path, raw_body, verify=True)
        return response

    def alert_delete(self, symbol, price):
        """`Bitfinex auth alert delete reference
        <https://docs.bitfinex.com/reference#rest-auth-alert-del>`_


        Bitfinex always returns [True] no matter if the request deleted an alert or not

        Parameters
        ----------
        symbol : str
            The `symbol <restv1.html#symbols>`_ you want information about.

        price : float
            Price where you want to receive alerts

        Returns
        -------
        list
             ::

                [ True ]

        Example
        -------
         ::

            bfx_client.alert_delete('tIOTUSD', 1)

        """
        body = {}

        raw_body = json.dumps(body)
        path = "v2/auth/w/alert/price:{}:{}/del".format(symbol, price)
        response = self._post(path, raw_body, verify=True)
        return response

    def calc_available_balance(self, symbol, direction, rate, order_type):
        """`Bitfinex calc balance available reference
        <https://docs.bitfinex.com/reference#rest-auth-calc-order-avail>`_

        Calculate available balance for order/offer
        example : calc_available_balance("tIOTUSD","1","1.13","EXCHANGE")

        Parameters
        ----------
        symbol : str
            The `symbol <restv1.html#symbols>`_ you want information about.

        dir : int
            direction of the order/offer
            (orders: > 0 buy, < 0 sell | offers: > 0 sell, < 0 buy)

        rate : string
            Rate of the order/offer

        type : string
            Type of the order/offer EXCHANGE or MARGIN

        Returns
        -------
        list
             ::

                [AMOUNT_AVAIL]

        Example
        -------
         ::

            bfx_client.calc_available_balance('tIOTUSD', 1, 0.02, 'EXCHANGE')

        """

        body = {
            'symbol': symbol,
            'dir': direction,
            'rate': rate,
            'type': order_type
        }

        raw_body = json.dumps(body)
        path = "v2/auth/calc/order/avail"
        response = self._post(path, raw_body, verify=True)
        return response

    def user_settings_write(self, pkey):
        """`Bitfinex user settings write reference
        <https://docs.bitfinex.com/reference#rest-auth-settings-set>`_

        Write user settings

        Warning
        -------
        Not Implemented

        """
        raise NotImplementedError

    def user_settings_read(self, pkey):
        """`Bitfinex user settings read reference
        <https://docs.bitfinex.com/reference#rest-auth-settings>`_

        Read user settings

        Parameters
        ----------
        pkey : str
            Requested Key

        Returns
        -------
        list
             ::

                [
                  [
                    KEY
                    VALUE
                  ],
                  ...
                ]

        Example
        --------
         ::

            none available

        """
        body = {
            'keys': ['api:{}'.format(pkey)]
        }
        raw_body = json.dumps(body)
        path = "v2/auth/r/settings"
        response = self._post(path, raw_body, verify=True)
        return response

    def user_settings_delete(self, pkey):
        """`Bitfinex user settings delete reference
        <https://docs.bitfinex.com/reference#rest-auth-settings-del>`_

        Delete user settings

        Warning
        -------
        Not Implemented

        """
        raise NotImplementedError
