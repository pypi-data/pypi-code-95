from pagarme import bank_account
from tests.resources.dictionaries import bank_account_dictionary


def test_create_bank_account():
    bank = bank_account.create(bank_account_dictionary.BANK_ACCOUNT)
    assert bank['id'] is not None


def test_find_all_bank_accounts():
    all_bank_accounts = bank_account.find_all()
    assert all_bank_accounts is not None


def test_find_by():
    bank = bank_account.create(bank_account_dictionary.BANK_ACCOUNT)
    search_params = {'id': str(bank['id'])}
    find_bank = bank_account.find_by(search_params)
    assert bank['id'] == find_bank[0]['id']
