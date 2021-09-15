from pagarme import card
from tests.resources.dictionaries import card_dictionary


def test_create_card():
    _card = card.create(card_dictionary.VALID_CARD)
    assert _card['id'] is not None


def test_find_all():
    cards = card.find_all()
    assert cards is not None


def test_find_by():
    _card = card.create(card_dictionary.VALID_CARD)
    search_params = {'id': _card['id']}
    find_card = card.find_by(search_params)
    assert _card['id'] == find_card[0]['id']
