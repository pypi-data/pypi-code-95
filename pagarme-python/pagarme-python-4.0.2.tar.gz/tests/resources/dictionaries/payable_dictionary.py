from pagarme import transaction
from tests.resources.dictionaries import transaction_dictionary

TRANSACTION = transaction.create(transaction_dictionary.VALID_CREDIT_CARD_TRANSACTION)

PAYABLES = transaction.payables(TRANSACTION['id'])
