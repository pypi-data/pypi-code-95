from pagarme import recipient
from tests.resources import pagarme_test
from tests.resources.dictionaries import card_dictionary
from tests.resources.dictionaries import customer_dictionary
from tests.resources.dictionaries import recipient_dictionary

BOLETO_TRANSACTION = {
    'amount': '1000000',
    'payment_method': 'boleto',
    'postback_url': pagarme_test.create_postback_url(),
    'customer': customer_dictionary.CUSTOMER,
}

CALCULATE_INTALLMENTS_AMOUNT = {
    'amount': '10000',
    'free_installments': "1",
    'interest_rate': '13',
    'max_installments': '12'
}

DEFAULT_RECIPIENT = recipient.default_recipient()['test']

RECIPIENT = recipient.create(recipient_dictionary.RECIPIENT)

SPLIT_RULE_AMOUNT = [
    {
        'recipient_id': DEFAULT_RECIPIENT,
        'amount': 500000,
        'liable': 'true',
        'charge_processing_fee': 'true'
    },
    {
        'recipient_id': RECIPIENT['id'],
        'amount': 500000,
        'liable': 'true',
        'charge_processing_fee': 'true'
    }
]

SPLIT_RULE_PERCENTAGE = [
    {
        'recipient_id': DEFAULT_RECIPIENT,
        'percentage': 50,
        'liable': 'true',
        'charge_processing_fee': 'true'
    },
    {
        'recipient_id': RECIPIENT['id'],
        'percentage': 50,
        'liable': 'true',
        'charge_processing_fee': 'true'
    }
]

BOLETO_TRANSACTION_SPLIT_RULE_PERCENTAGE = {
    'amount': BOLETO_TRANSACTION['amount'],
    'payment_method': BOLETO_TRANSACTION['payment_method'],
    'split_rules': SPLIT_RULE_PERCENTAGE,
    'customer': customer_dictionary.CUSTOMER,
}

INVALID_CREDIT_CARD_TRANSACTION = {
    'amount': '1000000',
    'card_number': card_dictionary.INVALID_CARD['card_number'],
    'card_holder_name': card_dictionary.INVALID_CARD['card_holder_name'],
    'card_cvv': card_dictionary.INVALID_CARD['card_cvv'],
    'card_expiration_date': card_dictionary.INVALID_CARD['card_expiration_date'],
    'customer': customer_dictionary.CUSTOMER
}

INVALID_REQUEST = {
    'amount': '1',
    'payment_method': BOLETO_TRANSACTION['payment_method'],
    'customer': customer_dictionary.CUSTOMER
}

PAY_BOLETO = {
    'status': 'paid'
}

REFUNDED_OR_CAPTURE_TRANSACTION = {
    'amount': '1000000'
}

VALID_CREDIT_CARD_TRANSACTION = {
    'amount': '1000000',
    'card_number': card_dictionary.VALID_CARD['card_number'],
    'card_holder_name': card_dictionary.VALID_CARD['card_holder_name'],
    'card_cvv': card_dictionary.VALID_CARD['card_cvv'],
    'card_expiration_date': card_dictionary.VALID_CARD['card_expiration_date'],
    'customer': customer_dictionary.CUSTOMER,
    'installments': '12'
}

VALID_CREDIT_CARD_TRANSACTION_CAPTURE_FALSE = {
    'amount': '1000000',
    'capture': 'false',
    'card_number': card_dictionary.VALID_CARD['card_number'],
    'card_holder_name': card_dictionary.VALID_CARD['card_holder_name'],
    'card_cvv': card_dictionary.VALID_CARD['card_cvv'],
    'card_expiration_date': card_dictionary.VALID_CARD['card_expiration_date'],
    'customer': customer_dictionary.CUSTOMER
}

VALID_CREDIT_CARD_TRANSACTION_WITH_POSTBACK = {
    'amount': '1000000',
    'card_number': card_dictionary.VALID_CARD['card_number'],
    'postback_url': pagarme_test.create_postback_url(),
    'card_holder_name': card_dictionary.VALID_CARD['card_holder_name'],
    'card_cvv': card_dictionary.VALID_CARD['card_cvv'],
    'card_expiration_date': card_dictionary.VALID_CARD['card_expiration_date'],
    'customer': customer_dictionary.CUSTOMER
}

VALID_CREDIT_CARD_TRANSACTION_WITH_SPLIT_RULE_AMOUNT = {
    'amount': '1000000',
    'card_number': card_dictionary.VALID_CARD['card_number'],
    'card_holder_name': card_dictionary.VALID_CARD['card_holder_name'],
    'card_cvv': card_dictionary.VALID_CARD['card_cvv'],
    'card_expiration_date': card_dictionary.VALID_CARD['card_expiration_date'],
    'customer': customer_dictionary.CUSTOMER,
    'split_rules': SPLIT_RULE_AMOUNT
}

VALID_CREDIT_CARD_TRANSACTION_WITH_SPLIT_RULE_PERCENTAGE = {
    'amount': '1000000',
    'card_number': card_dictionary.VALID_CARD['card_number'],
    'card_holder_name': card_dictionary.VALID_CARD['card_holder_name'],
    'card_cvv': card_dictionary.VALID_CARD['card_cvv'],
    'card_expiration_date': card_dictionary.VALID_CARD['card_expiration_date'],
    'customer': customer_dictionary.CUSTOMER,
    'split_rules': SPLIT_RULE_PERCENTAGE
}
