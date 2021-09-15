from pagarme import balance


def test_default_recipient_balance():
    _balance = balance.default_recipient_balance()
    assert _balance['object'] == 'balance'
    assert _balance['available']['amount'] == 993886
    assert _balance['waiting_funds']['amount'] == 950000
    assert _balance['transferred']['amount'] == 5000
