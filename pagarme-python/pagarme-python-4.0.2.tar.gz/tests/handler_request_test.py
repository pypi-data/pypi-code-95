from pagarme.resources import handler_request
from tests.resources.pagarme_test import AUTH_TEST


def test_authentication_key():
    auth = handler_request.authentication_key(AUTH_TEST['api_key'])
    assert auth['api_key'] == AUTH_TEST['api_key']
