import time
from pagarme import balance_operation
from pagarme import transaction
from pagarme import transfer
from tests.resources.dictionaries import transaction_dictionary
from tests.resources.dictionaries import transfer_dictionary


def test_find_all():
    boleto = transaction.create(transaction_dictionary.BOLETO_TRANSACTION_SPLIT_RULE_PERCENTAGE)
    transaction.pay_boleto(boleto['id'], transaction_dictionary.PAY_BOLETO)
    transfer_dictionary.TRANSFER['recipient_id'] = \
        transaction_dictionary.BOLETO_TRANSACTION_SPLIT_RULE_PERCENTAGE['split_rules'][0]['recipient_id']
    transfer.create(transfer_dictionary.TRANSFER)
    balance_operations = balance_operation.find_all()
    assert balance_operations is not None


def test_find_by():
    boleto = transaction.create(transaction_dictionary.BOLETO_TRANSACTION_SPLIT_RULE_PERCENTAGE)
    transaction.pay_boleto(boleto['id'], transaction_dictionary.PAY_BOLETO)
    time.sleep(4)
    transfer_dictionary.TRANSFER['recipient_id'] = \
        transaction_dictionary.BOLETO_TRANSACTION_SPLIT_RULE_PERCENTAGE['split_rules'][0]['recipient_id']
    transfer.create(transfer_dictionary.TRANSFER)
    find_all = balance_operation.find_all()
    search_params = {'id': find_all[0]['id']}
    find_balance_operation = balance_operation.find_by(search_params)
    assert find_balance_operation[0]['id'] == find_all[0]['id']
