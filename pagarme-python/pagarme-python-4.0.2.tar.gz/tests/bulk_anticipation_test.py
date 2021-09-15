from pagarme import bulk_anticipation
from pagarme import recipient
from pagarme import transaction
from tests.resources.dictionaries import bulk_anticipation_dictionary
from tests.resources.dictionaries import recipient_dictionary
from tests.resources.dictionaries import transaction_dictionary


def test_cancel():
    transaction.create(transaction_dictionary.VALID_CREDIT_CARD_TRANSACTION)
    default_recipient_id = transaction_dictionary.DEFAULT_RECIPIENT
    recipient.update_recipient(default_recipient_id, recipient_dictionary.UPDATE_RECIPIENT)
    _bulk_anticipation = bulk_anticipation.create(default_recipient_id, bulk_anticipation_dictionary.BULK_ANTICIPATION)
    bulk_anticipation.confirm(default_recipient_id, _bulk_anticipation['id'])
    cancel_bulk_anticipation = bulk_anticipation.cancel(default_recipient_id, _bulk_anticipation['id'])
    assert cancel_bulk_anticipation['status'] == 'canceled'


def test_confirm():
    transaction.create(transaction_dictionary.VALID_CREDIT_CARD_TRANSACTION)
    default_recipient_id = transaction_dictionary.DEFAULT_RECIPIENT
    recipient.update_recipient(default_recipient_id, recipient_dictionary.UPDATE_RECIPIENT)
    _bulk_anticipation = bulk_anticipation.create(default_recipient_id, bulk_anticipation_dictionary.BULK_ANTICIPATION)
    confirm_bulk_anticipation = bulk_anticipation.confirm(default_recipient_id, _bulk_anticipation['id'])
    assert confirm_bulk_anticipation['status'] == 'pending'


def test_create():
    transaction.create(transaction_dictionary.VALID_CREDIT_CARD_TRANSACTION)
    default_recipient_id = transaction_dictionary.DEFAULT_RECIPIENT
    recipient.update_recipient(default_recipient_id, recipient_dictionary.UPDATE_RECIPIENT)
    _bulk_anticipation = bulk_anticipation.create(default_recipient_id, bulk_anticipation_dictionary.BULK_ANTICIPATION)
    assert _bulk_anticipation['id'] is not None


def test_delete():
    transaction.create(transaction_dictionary.VALID_CREDIT_CARD_TRANSACTION)
    default_recipient_id = transaction_dictionary.DEFAULT_RECIPIENT
    recipient.update_recipient(default_recipient_id, recipient_dictionary.UPDATE_RECIPIENT)
    _bulk_anticipation = bulk_anticipation.create(default_recipient_id, bulk_anticipation_dictionary.BULK_ANTICIPATION)
    delete_bulk_anticiaption = bulk_anticipation.delete(default_recipient_id, _bulk_anticipation['id'])
    assert delete_bulk_anticiaption is not None


def test_find_all():
    transaction.create(transaction_dictionary.VALID_CREDIT_CARD_TRANSACTION)
    default_recipient_id = transaction_dictionary.DEFAULT_RECIPIENT
    recipient.update_recipient(default_recipient_id, recipient_dictionary.UPDATE_RECIPIENT)
    _bulk_anticipation = bulk_anticipation.create(default_recipient_id, bulk_anticipation_dictionary.BULK_ANTICIPATION)
    all_bulk_anticipations = bulk_anticipation.find_all(default_recipient_id)
    assert all_bulk_anticipations[0]['id'] == _bulk_anticipation['id']


def test_limits():
    default_recipient_id = transaction_dictionary.DEFAULT_RECIPIENT
    limits = bulk_anticipation.limits(default_recipient_id, bulk_anticipation_dictionary.LIMITS)
    assert limits['maximum']['amount'] == 3333360
    assert limits['minimum']['amount'] == 83334
