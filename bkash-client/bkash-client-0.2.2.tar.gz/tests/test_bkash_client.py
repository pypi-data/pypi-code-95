import os
import json
from pprint import pprint
from bkash_client.dataclasses.checkout import CreatePaymentResponse
from bkash_client.client import get_client
from bkash_client.dataclasses.base import ClientTypeEnum
from decimal import Decimal


IFRAME_CREDENTIALS = None
IFRAME_CREDENTIALS_PATH = os.environ.get("IFRAME_CREDENTIALS")
if IFRAME_CREDENTIALS_PATH:
    with open(IFRAME_CREDENTIALS_PATH, "r") as cf:
        IFRAME_CREDENTIALS = json.load(cf)


IFRAME_PAYMENT_CREATE_DATA = {"amount": "500", "merchantInvoiceNumber": "beta1000"}


def test_create_iframe_payment():

    client = get_client(IFRAME_CREDENTIALS, type=ClientTypeEnum.IFRAME_BASED)
    data = client.create_payment(IFRAME_PAYMENT_CREATE_DATA)

    assert isinstance(data, CreatePaymentResponse)
    assert data.amount == Decimal("500")
