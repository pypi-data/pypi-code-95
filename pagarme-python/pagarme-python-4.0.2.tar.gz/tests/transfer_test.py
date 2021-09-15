from pagarme import transaction
from pagarme import transfer
from tests.resources.dictionaries import transaction_dictionary
from tests.resources.dictionaries import transfer_dictionary


def test_cancel_transfer():
    boleto = transaction.create(transaction_dictionary.BOLETO_TRANSACTION_SPLIT_RULE_PERCENTAGE)
    transaction.pay_boleto(boleto['id'], transaction_dictionary.PAY_BOLETO)
    transfer_dictionary.TRANSFER['recipient_id'] = \
        transaction_dictionary.BOLETO_TRANSACTION_SPLIT_RULE_PERCENTAGE['split_rules'][0]['recipient_id']
    _transfer = transfer.create(transfer_dictionary.TRANSFER)
    search_params = {'id': str(_transfer['id'])}
    find_transfer = transfer.find_by(search_params)
    cancel_transfer = transfer.cancel(find_transfer[0]['id'])
    assert cancel_transfer['status'] == 'canceled'


def test_create_transfer():
    boleto = transaction.create(transaction_dictionary.BOLETO_TRANSACTION_SPLIT_RULE_PERCENTAGE)
    transaction.pay_boleto(boleto['id'], transaction_dictionary.PAY_BOLETO)
    transfer_dictionary.TRANSFER['recipient_id'] = \
        transaction_dictionary.BOLETO_TRANSACTION_SPLIT_RULE_PERCENTAGE['split_rules'][0]['recipient_id']
    _transfer = transfer.create(transfer_dictionary.TRANSFER)
    assert _transfer['id'] is not None


def test_find_all_transfers():
    all_transfers = transfer.find_all()
    assert all_transfers is not None


def test_find_by():
    boleto = transaction.create(transaction_dictionary.BOLETO_TRANSACTION_SPLIT_RULE_PERCENTAGE)
    transaction.pay_boleto(boleto['id'], transaction_dictionary.PAY_BOLETO)
    transfer_dictionary.TRANSFER['recipient_id'] = \
        transaction_dictionary.BOLETO_TRANSACTION_SPLIT_RULE_PERCENTAGE['split_rules'][0]['recipient_id']
    _transfer = transfer.create(transfer_dictionary.TRANSFER)
    search_params = {'id': str(_transfer['id'])}
    find_transfer = transfer.find_by(search_params)
    assert _transfer['id'] == find_transfer[0]['id']
