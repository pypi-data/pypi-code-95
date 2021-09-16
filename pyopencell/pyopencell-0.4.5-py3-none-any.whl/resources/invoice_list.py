from pyopencell.client import Client
from pyopencell.resources.base_resource_list import BaseResourceList
from pyopencell.resources.invoice import Invoice
from pyopencell.responses.paged_response import PagedResponse
from pyopencell.responses.action_status import ActionStatus


class InvoiceList(BaseResourceList):
    _name = "invoices"
    _url_path = "/invoice/list"
    items_resource_class = Invoice
    items_per_page = 10

    invoices = []

    @classmethod
    def get(cls, query=None, limit=None, offset=None):
        """
        Returns a Invoice list with invoice instances data.

        :return: PagedResponse:
        """
        if not limit:
            limit = cls.items_per_page

        response_data = Client().get(
            cls._url_path,
            query=query,
            limit=limit,
            offset=offset
        )

        status = response_data.get("status")
        if status and status != "SUCCESS":
            return ActionStatus(**response_data)

        return PagedResponse(cls, **response_data)

    @classmethod
    def filter_by_date(cls, date, limit=None, offset=None):
        """
        Returns a Invoice list with invoice instances data.
        Filtering the invoices by date

        :arg date: Datetime
        :return: PagedResponse:
        """
        query = "invoiceDate:{}".format(date.strftime("%Y-%m-%d"))
        return cls.get(query=query, limit=limit, offset=offset)
