from typing import Tuple, Optional, Dict, Callable

import zeep
from zeep.exceptions import Fault, XMLSyntaxError
from zeep.helpers import serialize_object
from .exceptions import EXCEPTION_MAP, OtherError, ServiceDown
from requests.exceptions import ConnectionError
from zeep.cache import SqliteCache
from zeep.transports import Transport


PROD_WSDL = "http://ec.europa.eu/taxation_customs/vies/checkVatService.wsdl"
TEST_WSDL = "http://ec.europa.eu/taxation_customs/vies/checkVatTestService.wsdl"

Response = Tuple[bool, Optional[Dict]]


class Client(object):
    def __init__(
        self,
        wsdl: str = PROD_WSDL,
        cache_path: Optional[str] = None,
        cache_timeout: Optional[int] = None,
    ) -> None:
        try:
            cache = SqliteCache(path=cache_path, timeout=cache_timeout)
            transport = Transport(cache=cache)
            self.zeep = zeep.Client(wsdl, transport=transport)

        except ConnectionError as e:
            # Failed to fetch wsdl
            raise ServiceDown(str(e))

    def _request(self, method: Callable, **arguments) -> Response:
        try:
            response = method(**arguments)
            return response.valid, serialize_object(response, dict)
        except Fault as error:
            try:
                raise EXCEPTION_MAP[error.message]
            except KeyError:
                raise OtherError
        except XMLSyntaxError as e:
            raise ServiceDown(str(e))

    def check(self, country_code: str, vat_number: str) -> Response:
        return self._request(
            self.zeep.service.checkVat, countryCode=country_code, vatNumber=vat_number
        )

    def check_approx(
        self,
        country_code: str,
        vat_number: str,
        trader_name: Optional[str] = None,
        trader_company_type: Optional[str] = None,  # tns1:traderCompanyType @TODO
        trader_street: Optional[str] = None,
        trader_postcode: Optional[str] = None,
        trader_city: Optional[str] = None,
        requester_country_code: Optional[str] = None,
        requester_vat_number: Optional[str] = None,
    ) -> Response:

        return self._request(
            self.zeep.service.checkVatApprox,
            countryCode=country_code,
            vatNumber=vat_number,
            traderName=trader_name,
            traderCompanyType=trader_company_type,
            traderStreet=trader_street,
            traderPostcode=trader_postcode,
            traderCity=trader_city,
            requesterCountryCode=requester_country_code,
            requesterVatNumber=requester_vat_number,
        )
