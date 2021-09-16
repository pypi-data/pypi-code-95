from pyopencell.client import Client
from pyopencell.resources.base_resource import BaseResource
from pyopencell.responses.response import ActionStatus


class Invoice(BaseResource):
    _name = "invoice"
    _url_path = "/invoice"

    invoiceId = 0
    invoiceType = ""
    billingAccountCode = ""
    sellerCode = ""
    subscriptionCode = ""
    orderNumber = ""
    dueDate = 0
    invoiceDate = 0
    categoryInvoiceAgregate = [{}]
    taxAggregate = [{}]
    invoiceNumber = ""
    amountWithoutTax = 0
    amountTax = 0
    amountWithTax = 0
    paymentMethod = "DIRECTDEBIT"
    pdfFilename = ""
    pdf = ""
    netToPay = 0
    invoiceMode = "DETAILLED"
    dueBalance = 0
    isDraft = True

    @classmethod
    def sendByEmail(cls, invoice_id):
        """
        Send the invoice by email

        :return:
        """
        response_data = Client().post(
            "{}/{}".format(cls._url_path, "sendByEmail"),
            {
                "invoiceId": invoice_id,
            })
        return ActionStatus(**response_data)
