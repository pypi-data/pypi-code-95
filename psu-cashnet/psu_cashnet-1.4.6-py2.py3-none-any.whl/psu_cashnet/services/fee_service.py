from psu_base.services import utility_service, auth_service, error_service
from django.db.models.query import QuerySet
from psu_base.classes.Log import Log
from psu_cashnet.models.transaction import Transaction
from psu_cashnet.models.purchase import PurchasedItem
from psu_cashnet.models.catalog import CatalogItem


log = Log()


def get_fee_dict():
    fee_dict = utility_service.recall()
    if fee_dict:
        return fee_dict
    else:
        fee_dict = {}

    fees = CatalogItem.objects.filter(app_code=utility_service.get_app_code())
    for fee in fees:
        fee_dict[fee.item_code] = fee
    return utility_service.store(fee_dict)
