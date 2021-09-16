from pyopencell.client import Client
from pyopencell.resources.base_resource import BaseResource
from pyopencell.responses.action_status import ActionStatus


class CRMAccountHierarchy(BaseResource):
    _url_path = "/account/accountHierarchy"

    crmAccountType = ""
    crmParentCode = ""
    code = ""
    description = ""
    externalRef1 = ""
    externalRef2 = ""
    name = {
        "title": "",
        "firstName": "",
        "lastName": "",
    }
    address = {
        "address1": "",
        "address2": "",
        "address3": "",
        "zipCode": "",
        "city": "",
        "country": "",
        "state": ""
    }
    contactInformation = {
        "email": "",
        "phone": "",
        "mobile": "",
        "fax": ""
    }
    jobTitle = ""
    language = ""
    terminationReason = ""
    subscriptionDate = None
    terminationDate = None
    customerCategory = ""
    customerBrand = ""
    registrationNo = ""
    vatNo = ""
    mandateIdentification = ""
    mandateDate = None
    currency = ""
    # TODO: Create this list of values in the resource CustomerAccount
    caStatus = ""  # Possible value: 'ACTIVE' or 'CLOSE'
    creditCategory = ""
    dateStatus = None
    dateDunningLevel = None
    # TODO: Create this list of values in the resource Dunning if is needed.
    dunningLevel = ""  # Possible value: 'R0', 'R1', 'R2', 'R3' or 'R4'
    methodOfPayment = []
    billingCycle = ""
    country = ""
    nextInvoiceDate = None
    electronicBilling = False
    # TODO: Create this list of values in the resource BillingAccount
    baStatus = ""  # Possibles values: 'ACTIVE', 'CANCELED', 'TERMINATED' or 'CLOSED'
    email = ""
    invoicingThreshold = None
    # TODO: Create this list of values in the resource UserAccount
    uaStatus = ""  # Possibles values: 'ACTIVE', 'CANCELED', 'TERMINATED' or 'CLOSED'
    cfToAdd = {}
    cfMapToAdd = {}
    customFields = []
    discountPlanForInstantiation = []
    discountPlanForTermination = []

    @classmethod
    def create(cls, **kwargs):
        """
        Creates a CRMAccountHierarchy instance.
        This resource in OpenCell is not a single resource, is a hierarchy os resources,
        from Customer to User Account.

        :param kwargs:
        :return:
        """
        response_data = Client().post(
            "{}/{}".format(cls._url_path, 'createCRMAccountHierarchy'),
            body=kwargs)

        return ActionStatus(**response_data)

    @classmethod
    def update(cls, **kwargs):
        """
        Update a CRMAccountHierarchy instance.

        :param kwargs:
        :return:
        """
        response_data = Client().post(
            "{}/{}".format(cls._url_path, 'createOrUpdateCRMAccountHierarchy'),
            body=kwargs)

        return ActionStatus(**response_data)
