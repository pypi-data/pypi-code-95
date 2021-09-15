from pagarme import payable
from tests.resources.dictionaries import payable_dictionary

def test_find_all_payables():
    all_payables = payable.find_all()
    assert all_payables is not None


def test_find_by():
    search_params = {'id': str(payable_dictionary.PAYABLES[0]['id'])}
    find_payable = payable.find_by(search_params)
    assert str(find_payable[0]['id']) == search_params['id']