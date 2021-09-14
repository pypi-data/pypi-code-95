# coding: utf-8
import unittest

from otrs_somconnexio.otrs_models.mobile_data import MobileData


class MobileDataTestCase(unittest.TestCase):

    def test_init(self):
        mobile_data = MobileData(
            order_id=123,
            phone_number="666666666",
            iban="ES6621000418401234567891",
            email="test@test.com",
            previous_provider="SC",
            previous_owner_vat="740227654G",
            previous_owner_name="name",
            previous_owner_surname="surname",
            portability=False,
            sc_icc="123456789",
            icc=None,
            product="product",
            notes="Mobile crm lead line",
        )

        self.assertIsInstance(mobile_data, MobileData)
