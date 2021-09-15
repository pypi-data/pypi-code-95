from pagarme import payment_link
from tests.resources.dictionaries import payment_link_dictionary
import pytest
import time

def test_cancel_payment_link():
    pl = payment_link.create(payment_link_dictionary.VALID_PAYMENT_LINK)
    cancel_payment_link = payment_link.cancel(pl['id'])
    assert 'canceled' == cancel_payment_link['status']

def test_create_payment_link():
    pl = payment_link.create(payment_link_dictionary.VALID_PAYMENT_LINK)
    assert pl['id'] is not None

def test_error_request():
    with pytest.raises(Exception) as PagarMeException:
        payment_link.create(payment_link_dictionary.INVALID_REQUEST)
    assert 'amount' in str(PagarMeException.value)

def test_find_all_payment_links():
    all_payment_links = payment_link.find_all()
    assert all_payment_links is not None

def test_find_by(retry):
    pl = payment_link.create(payment_link_dictionary.VALID_PAYMENT_LINK)
    search_params = {'id': pl['id']}
    find_pl = retry(lambda: payment_link.find_by(search_params))
    assert pl['id'] == find_pl[0]['id']

def test_find_by_id(retry):
    pl = payment_link.create(payment_link_dictionary.VALID_PAYMENT_LINK)
    found_pl = retry(lambda: payment_link.find_by_id(pl['id']))
    assert pl['id'] == found_pl['id']

def test_update():
    pl = payment_link.create(payment_link_dictionary.VALID_PAYMENT_LINK)
    updated_payment_link = payment_link.update_by_id(pl['id'], payment_link_dictionary.UPDATE_NAME)
    assert 'aqueles pique link pago' == updated_payment_link['name']
