from pyopencell.client import Client
from pyopencell.resources.base_resource import BaseResource
from pyopencell.responses.response import Response, ActionStatus


class Customer(BaseResource):
    _name = "customer"
    _url_path = "/account/customer"

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
    customerCategory = ""
    name = {
        "title": "",
        "firstName": "",
        "lastName": "",
    }
    updatedCode = ""
    customerBrand = ""
    jobTitle = ""
    seller = ""
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
    mandateIdentification = ""
    customFields = []
    mandateDate = None
    vatNo = ""
    additionalDetails = {
        "companyName": "",
        "positon": "",
        "instantMessengers": "",
    }
    registrationNo = ""
    contactInformation = {
        "email": "",
        "phone": "",
        "mobile": "",
        "fax": "",
    }
    customerAccounts = {
        "customerAccount": []
    }

    @classmethod
    def get(cls, customerCode):
        """
        Returns a customer instance obtained by id.

        :param id:
        :return: Customer:
        """
        response_data = Client().get(cls._url_path, customerCode=customerCode)

        status = response_data.get("status")
        if status and status != "SUCCESS":
            return ActionStatus(**response_data)

        return Response(cls, **response_data)

    @classmethod
    def create(cls, **kwargs):
        """
        Creates a customer instance.

        :param kwargs:
        :return:
        """
        response_data = Client().post(cls._url_path, kwargs)

        return ActionStatus(**response_data)

    @classmethod
    def update(cls, **kwargs):
        """
        Creates a customer instance.

        :param kwargs:
        :return:
        """
        response_data = Client().put(cls._url_path, kwargs)

        return ActionStatus(**response_data)
