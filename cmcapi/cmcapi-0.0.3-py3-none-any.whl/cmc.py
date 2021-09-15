import json

from requests import Session

from .log import logger_

BASE_URL = 'https://pro-api.coinmarketcap.com/'
API_VERSION = 'v1'
# ---API endpoints for cmc cryptocurrency--- #
LATEST_LISTINGS = '/cryptocurrency/listings/latest'


class Response(object):
    """wrap response"""

    def __init__(self, resp):
        self._payload = json.loads(resp.text)
        self.status = self._payload.get('status', {})
        self.data = self._payload.get('data', {})
        self.status_code = self._payload.get('statusCode', None)
        self.time_samp = self.status.get('timestamp', None)
        self.error_code = self.status.get('error_code', None)
        self.error_message = self.status.get('error_message', None)
        self.elapsed = self.status.get('elapsed', None)
        self.credit_count = self.status.get('credit_count', None)


class CoinMarketCapAPI(object):
    """CoinMarketCapAPI Wrapper Class"""

    def __init__(self, api_key=None, **kwargs):
        self._logger = kwargs.get('logger', logger_)
        self._session = Session()
        self._base_url = BASE_URL
        self._version = API_VERSION
        self._pre_url = self._base_url + self._version
        self._headers = {
            'Accepts': 'application/json',
            'Accept-Encoding': 'deflate, gzip',
            'X-CMC_PRO_API_KEY': api_key
        }

    def _get(self, url, **kwargs):

        self._session.headers.update(self._headers)
        url = '{}{}'.format(self._pre_url, url)

        try:
            response = self._session.get(url, params=kwargs)
            rep = Response(response)
            return rep
        except Exception as e:
            raise e

    def listings_latest(self, **kwargs):
        """
          Latest listings
          See: https://coinmarketcap.com/api/documentation/v1/#operation/getV1CryptocurrencyListingsLatest
        """
        self._logger.info('calling src api: {}'.format(LATEST_LISTINGS))
        return self._get(LATEST_LISTINGS, **kwargs)
