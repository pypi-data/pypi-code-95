from tests.resources import pagarme_test

VALID_PAYMENT_LINK = {
    'amount': 1000,
    'items': [
        {
            'id': '1',
            'title': 'Bola de futebol',
            'unit_price': 400,
            'quantity': 1,
            'tangible': True
        },
        {
            'id': 'a123',
            'title': 'Caderno do Goku',
            'unit_price': 600,
            'quantity': 1,
            'tangible': True
        }
    ]
}

INVALID_REQUEST = {
    'amount': '1'
}

UPDATE_NAME = {
    'name': 'aqueles pique link pago'
}
