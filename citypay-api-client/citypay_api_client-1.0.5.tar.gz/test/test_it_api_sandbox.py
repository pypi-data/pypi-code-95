# coding: utf-8

from __future__ import absolute_import
import unittest
import uuid
import citypay
from citypay.model.api_key import *


class TestApiIntegration(unittest.TestCase):
    """Error unit test stubs"""

    @classmethod
    def setUpClass(self):

        if 'CP_CLIENT_ID' not in os.environ:
            raise Exception("No CP_CLIENT_ID set")

        if 'CP_LICENCE_KEY' not in os.environ:
            raise Exception("No CP_LICENCE_KEY set")

        if 'CP_MERCHANT_ID' not in os.environ:
            raise Exception("No CP_MERCHANT_ID set")

        self.client_id = os.environ['CP_CLIENT_ID']
        self.licence_key = os.environ['CP_LICENCE_KEY']
        self.merchant_id = os.environ['CP_MERCHANT_ID']

        # create new api key on each call
        client_api_key = api_key_generate(self.client_id, self.licence_key)
        self.api_client = citypay.ApiClient(citypay.Configuration(
            host="https://sandbox.citypay.com/v6",
            api_key={'cp-api-key': str(client_api_key)}
        ))

    def testPing(self):
        api_response = citypay.OperationalApi(self.api_client).ping_request(citypay.Ping(
            identifier="it_test"
        ))
        self.assertEqual("044", api_response.code)
        self.assertEqual("it_test", api_response.identifier)
        self.assertEqual("Ping OK", api_response.message)
        self.assertIsNotNone(api_response.context)

    def testListMerchants(self):
        api_list_merchants = citypay.OperationalApi(self.api_client).list_merchants_request(self.client_id)
        self.assertEqual(api_list_merchants.clientid, str(self.client_id))

    def testAuthorise(self):

        id = uuid.uuid4().hex
        decision = citypay.PaymentProcessingApi(self.api_client).authorisation_request(citypay.AuthRequest(
            amount=1395,
            cardnumber="4000 0000 0000 0002",
            expmonth=12,
            expyear=2030,
            csc="012",
            identifier=id,
            merchantid=int(self.merchant_id)
        ))

        self.assertIsNone(decision.authen_required)
        self.assertIsNone(decision.request_challenged)
        self.assertIsNotNone(decision.auth_response)

        response = decision.auth_response
        self.assertEqual(response.result_code, "001")
        self.assertEqual(response.identifier, id)
        self.assertEqual(response.authcode, "A12345")
        self.assertEqual(response.amount, 1395)

    def testCardHolderAccounts(self):

        cha_id = uuid.uuid4().hex
        api = citypay.CardHolderAccountApi(self.api_client)
        result = api.account_create(citypay.AccountCreate(
            account_id=cha_id,
            contact=citypay.ContactDetails(
                address1="7 Esplanade",
                area="St Helier",
                company="CityPay Limited",
                country="JE",
                email="dev@citypay.com",
                firstname="Integration",
                lastname="Test",
                postcode="JE2 3QA"
            )
        ))

        self.assertEqual(result.account_id, cha_id)
        self.assertEqual(result.contact.address1, "7 Esplanade")

        result = api.account_card_register_request(cha_id, citypay.RegisterCard(
            cardnumber="4000 0000 0000 0002",
            expmonth=12,
            expyear=2030
        ))
        self.assertEqual(result.account_id, cha_id)
        self.assertEqual(len(result.cards), 1)
        self.assertEqual(result.cards[0].expmonth, 12)
        self.assertEqual(result.cards[0].expyear, 2030)

        result = api.account_retrieve_request(cha_id)
        self.assertEqual(result.account_id, cha_id)
        self.assertEqual(result.contact.address1, "7 Esplanade")
        self.assertEqual(len(result.cards), 1)
        self.assertEqual(result.cards[0].expmonth, 12)
        self.assertEqual(result.cards[0].expyear, 2030)

        identifier = uuid.uuid4().hex
        decision = api.charge_request(citypay.ChargeRequest(
            amount=7801,
            identifier=identifier,
            merchantid=int(self.merchant_id),
            token=result.cards[0].token,
            csc="012"
        ))

        self.assertIsNone(decision.authen_required)
        self.assertFalse(decision.is_authen_required())
        self.assertIsNone(decision.request_challenged)
        self.assertFalse(decision.is_request_challenged())
        self.assertIsNotNone(decision.auth_response)
        self.assertTrue(decision.is_auth_response())

        response = decision.auth_response
        self.assertEqual(response.result_code, "001")
        self.assertEqual(response.identifier, identifier)
        self.assertEqual(response.authcode, "A12345")
        self.assertEqual(response.amount, 7801)

        # attempt with 3dsv1
        identifier = uuid.uuid4().hex
        decision = api.charge_request(citypay.ChargeRequest(
            amount=7802,
            identifier=identifier,
            merchantid=int(self.merchant_id),
            token=result.cards[0].token,
            csc="801",
            trans_type='A',
            threedsecure=citypay.ThreeDSecure(
                accept_headers="text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                merchant_termurl="https://citypay.com/example-url",
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
                downgrade1=True
            )
        ))

        self.assertIsNotNone(decision.authen_required)
        self.assertTrue(decision.is_authen_required())
        self.assertIsNone(decision.request_challenged)
        self.assertFalse(decision.is_request_challenged())
        self.assertIsNone(decision.auth_response)
        self.assertFalse(decision.is_auth_response())

        self.assertIsNotNone(decision.authen_required.acs_url)
        self.assertIsNotNone(decision.authen_required.md)
        self.assertIsNotNone(decision.authen_required.pareq)

        result = api.account_delete_request(cha_id)
        self.assertEqual(result.code, "001")

    def tearDown(self):
        self.api_client.close()


if __name__ == '__main__':
    unittest.main()
