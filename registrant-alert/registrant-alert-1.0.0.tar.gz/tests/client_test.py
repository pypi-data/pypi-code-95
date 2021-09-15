import datetime
import os
import unittest
from registrantalert import Client, Fields
from registrantalert import ParameterError, ApiAuthError


class TestClient(unittest.TestCase):
    """
    Final integration tests without mocks.

    Active API_KEY is required.
    """

    def setUp(self) -> None:
        self.client = Client(os.getenv('API_KEY'))
        self.correct_basic_terms = {
            'include': ['app'],
            'exclude': ['blog']
        }

        self.correct_advanced_terms = [
            {
                'field': Fields.registrant_contact_organization,
                'term': "Airbnb, Inc."
            }
        ]

        self.incorrect_basic_terms = {
            'include': []
        }

        self.incorrect_advanced_terms = [
            {
                'field': 'abrakadabra'
            }
        ]

    def test_get_correct_data(self):
        response = self.client.data(
            basic_terms=self.correct_basic_terms,
            mode=Client.PURCHASE_MODE,
        )
        self.assertIsNotNone(response.domains_count)

    def test_extra_parameters(self):
        response = self.client.data(
            basic_terms=self.correct_basic_terms,
            mode=Client.PREVIEW_MODE,
            since_date=datetime.date.today() - datetime.timedelta(days=10),
            created_date_from=datetime.date(year=2019, month=1, day=1)
        )
        self.assertIsNotNone(response.domains_count)

    def test_empty_terms(self):
        with self.assertRaises(ParameterError):
            self.client.data()

    def test_empty_api_key(self):
        with self.assertRaises(ParameterError):
            client = Client('')
            client.data(basic_terms=self.correct_basic_terms)

    def test_incorrect_api_key(self):
        client = Client('at_00000000000000000000000000000')
        with self.assertRaises(ApiAuthError):
            client.data(basic_terms=self.correct_basic_terms)

    def test_raw_data(self):
        response = self.client.raw_data(
            basic_terms=self.correct_basic_terms,
            response_format=Client.XML_FORMAT)
        self.assertTrue(response.startswith('<?xml'))

    def test_advanced(self):
        response = self.client.data(
            advanced_terms=self.correct_advanced_terms
        )
        self.assertIsNotNone(response.domains_count)

    def test_incorrect_basic(self):
        with self.assertRaises(ParameterError):
            self.client.data(basic_terms=self.incorrect_basic_terms)

    def test_incorrect_advanced(self):
        with self.assertRaises(ParameterError):
            self.client.data(advanced_terms=self.incorrect_advanced_terms)

    def test_preview(self):
        response = self.client.preview(basic_terms=self.correct_basic_terms)
        self.assertGreater(response.domains_count, 0)

    def test_purchase(self):
        response = self.client.purchase(basic_terms=self.correct_basic_terms)
        self.assertGreater(len(response.domains_list), 0)

    def test_incorrect_date(self):
        with self.assertRaises(ParameterError):
            self.client.data(basic_terms=self.correct_basic_terms,
                             punicode='true',
                             updated_date_from='2020-01-01',
                             expired_date_to='19-19-19')

    def test_punycode(self):
        with self.assertRaises(ParameterError):
            self.client.data(advanced_terms=self.correct_advanced_terms,
                             punycode='not sure')

    def test_output(self):
        with self.assertRaises(ParameterError):
            self.client.data(advanced_terms=self.correct_advanced_terms,
                             output_format='yaml')


if __name__ == '__main__':
    unittest.main()
