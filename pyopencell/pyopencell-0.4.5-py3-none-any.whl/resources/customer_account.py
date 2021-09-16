from pyopencell.client import Client
from pyopencell.resources.base_resource import BaseResource
from pyopencell.responses.response import Response, ActionStatus


class CustomerAccount(BaseResource):
    _name = "customerAccount"
    _url_path = "/account/customerAccount"

    auditable = {
        "created": None,
        "updated": None,
        "creator": "",
        "updater": "",
    }
    id = None
    code = ""
    externalRef1 = ""
    externalRef2 = ""
    description = ""
    name = {
        "title": "",
        "firstName": "",
        "lastName": "",
    }
    jobTitle = ""
    updatedCode = ""
    businessAccountModel = {
        "auditable": {
            "created": None,
            "updated": None,
            "creator": "",
            "updater": "",
        },
        "id": None,
        "code": "",
        "description": "",
        "updatedCode": "",
    }
    contactInformation = {
        "email": "",
        "phone": "",
        "mobile": "",
        "fax": "",
    }
    vatNo = ""
    language = ""
    # TODO  Create this resource methodPayment
    methodOfPayment = {
        "paymentMethodType": "CARD",
        "id": 12345,
        "disabled": True,
        "alias": "...",
        "preferred": True,
        "customerAccountCode": "...",
        "info1": "...",
        "info2": "...",
        "info3": "...",
        "info4": "...",
        "info5": "...",
        "bankCoordinates": {
            "bankCode": "...",
            "branchCode": "...",
            "accountNumber": "...",
            "key": "...",
            "iban": "...",
            "bic": "...",
            "accountOwner": "...",
            "bankName": "...",
            "bankId": "...",
            "issuerNumber": "...",
            "issuerName": "...",
            "ics": "..."
        },
        "mandateIdentification": "...",
        "mandateDate": 12345,
        "cardType": "CB",
        "owner": "...",
        "monthExpiration": 12345,
        "yearExpiration": 12345,
        "tokenId": "...",
        "cardNumber": "...",
        "issueNumber": "...",
        "userId": "..."
    }
    customFields = []
    additionalDetails = {
        "companyName": "",
        "positon": "",
        "instantMessengers": "",
    }
    registrationNo = ""
    billingAccounts = {
        "billingAccount": []
    }
    status = ""

    @classmethod
    def get(cls, customerAccountCode):
        """
        Returns a customer instance obtained by id.

        :param id:
        :return: CustomerAccount:
        """
        response_data = Client().get(cls._url_path, customerAccountCode=customerAccountCode)

        status = response_data.get("status")
        if status and status != "SUCCESS":
            return ActionStatus(**response_data)

        return Response(cls, **response_data)
