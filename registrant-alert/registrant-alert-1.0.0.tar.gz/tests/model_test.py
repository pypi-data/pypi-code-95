import unittest
from json import loads
from registrantalert import Response, ErrorMessage


_json_response_ok_empty = '''{
   "domainsCount": 0,
    "domainsList": []
}'''

_json_response_ok = '''{
   "domainsCount": 2,
   "domainsList": [
        {
            "domainName": "villas-montego-bay.com",
            "date": "2021-09-13",
            "action": "added"
        },
        {
            "domainName": "airbnb-checkin-rooms1511.com",
            "date": "2021-09-14",
            "action": "dropped"
        }
    ]
}'''

_json_response_error = '''{
    "code": 403,
    "messages": "Access restricted. Check credits balance or enter the correct API key."
}'''


class TestModel(unittest.TestCase):

    def test_response_parsing(self):
        response = loads(_json_response_ok)
        parsed = Response(response)
        self.assertEqual(parsed.domains_count, response['domainsCount'])
        self.assertIsInstance(parsed.domains_list, list)
        self.assertEqual(
            parsed.domains_list[0].domain_name,
            response['domainsList'][0]['domainName'])

    def test_ok_with_dates(self):
        response = loads(_json_response_ok)
        parsed = Response(response)
        self.assertEqual(parsed.domains_count, response['domainsCount'])
        self.assertIsInstance(parsed.domains_list, list)
        self.assertEqual(
            parsed.domains_list[1].domain_name,
            response['domainsList'][1]['domainName'])
        self.assertEqual(
            parsed.domains_list[1].date.strftime(
                "%Y-%m-%d"),
            ''.join(response['domainsList'][1]['date']
                    .rsplit(':', 1))
        )
        self.assertEqual(
            parsed.domains_list[1].action,
            ''.join(response['domainsList'][1]['action']
                    .rsplit(':', 1))
        )

    def test_error_parsing(self):
        error = loads(_json_response_error)
        parsed_error = ErrorMessage(error)
        self.assertEqual(parsed_error.code, error['code'])
        self.assertEqual(parsed_error.message, error['messages'])
