"""
This is the only service that needs to be accessed from outside applications.

These functions will mostly be pointers to other functions in the Cashnet module
"""

from psu_base.classes.Log import Log
from psu_cashnet.services import transaction_service, fee_service

log = Log()


def get_transaction(transaction_id):
    return transaction_service.get_transaction(transaction_id)


def get_transaction_queryset():
    return transaction_service.get_transaction_queryset()


def create_transaction(
    requested_items,
    success_url,
    failure_url,
    merchant_code=None,
    reference_class=None,
    reference_id=None,
    secret_key=None,
    term_code=None,
):
    """Create a Cashnet Transaction record prior to sending customer to Cashnet"""
    return transaction_service.create_transaction(
        requested_items=requested_items,
        success_url=success_url,
        failure_url=failure_url,
        merchant_code=merchant_code,
        reference_class=reference_class,
        reference_id=reference_id,
        secret_key=secret_key,
        term_code=term_code,
    )


def cashnet_redirect(tx):
    """Prepare to redirect customer to cashnet. Returns the appropriate Cashnet URL"""
    return transaction_service.cashnet_redirect(tx)


def get_processed_transaction():
    """Get the transaction that was just processed (from flash scope)"""
    return transaction_service.get_processed_transaction()


def set_post_payment_processing_status(tx, status):
    """Indicate the status of post-payment processing"""
    log.trace([tx, status])
    tx.post_processing_status = str(status).strip()[:30] if status else status
    tx.save()


def get_fee_dict():
    """Get a dict of defined Cashnet Fees (catalog items) with the fee_code as the key"""
    return fee_service.get_fee_dict()
