from unittest import TestCase
from fastapi.exceptions import HTTPException

from fastapi_pagination import PaginationDetails, encode_cursor, decode_cursor


class PaginationDetailsTestCase(TestCase):

    def test_will_return_defaults_for_no_cursor_or_page_size(self):
        pagination_details = PaginationDetails()
        self.assertEqual(pagination_details.offset, 0)
        self.assertEqual(pagination_details.page_size, 200)

    def test_will_use_cursor(self):
        pagination_details = PaginationDetails(encode_cursor(100))
        self.assertEqual(pagination_details.offset, 100)
        self.assertEqual(pagination_details.page_size, 200)

    def test_will_throw_with_bad_cursor(self):
        with self.assertRaises(HTTPException):
            PaginationDetails('Bad')

    def test_will_use_page_size(self):
        pagination_details = PaginationDetails(encode_cursor(2), 150)
        self.assertEqual(pagination_details.offset, 2)
        self.assertEqual(pagination_details.page_size, 150)

    def test_will_limit_page_size(self):
        pagination_details = PaginationDetails(None, 10023)
        self.assertEqual(pagination_details.page_size, 999)

    def test_pagination_details_give_next_cursor(self):
        pagination = PaginationDetails(encode_cursor(100), 50)
        self.assertEqual(decode_cursor(pagination.next_cursor()), 150)

    def test_pagination_details_limit_page_size(self):
        pagination = PaginationDetails(None, 1100)
        self.assertEqual(decode_cursor(pagination.next_cursor()), 999)

    def test_pagination_details_gives_previous_cursor(self):
        pagination = PaginationDetails(encode_cursor(1000), 500)
        self.assertEqual(decode_cursor(pagination.previous_cursor()), 500)

    def test_pagination_details_limits_to_zero(self):
        pagination = PaginationDetails(encode_cursor(100), 500)
        self.assertEqual(decode_cursor(pagination.previous_cursor()), 0)

    def test_pagination_details_gives_no_cursor_for_no_last_page(self):
        pagination = PaginationDetails(None, 500)
        self.assertIsNone(pagination.previous_cursor())


class CursorEncodingTestCase(TestCase):

    def test_will_decode_encode_cursor(self):
        self.assertEqual(
            decode_cursor(encode_cursor(11234)),
            11234
        )

    def test_will_throw_with_invalid_cursor(self):
        with self.assertRaisesRegex(ValueError, 'Invalid cursor: bad-cursor'):
            decode_cursor('bad-cursor')
