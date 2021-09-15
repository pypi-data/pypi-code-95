from AsteriskRealtimeData.domain.mascara_ipaddress.mascara_ipaddress_search_criteria_vo import (
    MascaraIpaddressSearchCriteriaVo,
)
from AsteriskRealtimeData.application.mascara_ipaddress_service import MascaraIpaddressService
import ipaddress
import unittest

from AsteriskRealtimeData.domain.call.call_search_criteria_vo import CallSerchCriteriaVo


class TestSearchCriteriaVo(unittest.TestCase):
    def test_call_search_by_criteria_vo(self):
        search_one_term = CallSerchCriteriaVo(peer_name="SIP/100", origin_channel="123")
        print(search_one_term.as_dict())

    def test_ipaddress_search_by_criteria_vo(self):
        ipaddress_vo = MascaraIpaddressService().get_by_search_criteria(
            MascaraIpaddressSearchCriteriaVo(ipaddress="127.0.0.1")
        )
        print(ipaddress_vo)
