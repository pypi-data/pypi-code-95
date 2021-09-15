import unittest
import opps_sdk
from tests.conftest import *


class TestPayment(unittest.TestCase):

    def setUp(self):
        opps_sdk.opps_client.mer_config = opps_sdk.MerConfig(private_key, public_key, sys_id)
        print("setup")

    def tearDown(self):
        print("tearDown")

    def test_payment_create(self):
        print("test1")
        result = opps_sdk.ScanPayment.create(huifu_id=merchant_id, trade_type="A_NATIVE", trans_amt="1.00",
                                             goods_desc="test", notify_url="http")
        print(result)


