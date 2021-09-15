from pagarme import refund
from pagarme import transaction
from tests.resources.dictionaries import transaction_dictionary


def test_refunds():
    trx = transaction.create(transaction_dictionary.VALID_CREDIT_CARD_TRANSACTION)
    transaction.refund(trx['id'], transaction_dictionary.REFUNDED_OR_CAPTURE_TRANSACTION)
    refunds = refund.refunds()
    assert refunds[0]['status'] == 'refunded'
