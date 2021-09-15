from tests.resources.pagarme_test import generate_timestamp

BULK_ANTICIPATION = {
    'payment_date': generate_timestamp(),
    'timeframe': 'start',
    'requested_amount': '500000',
    'build': 'true'
}

LIMITS = {
    'payment_date': generate_timestamp(),
    'timeframe': 'start'
}
