from pyopencell.client import Client
from pyopencell.resources.base_resource import BaseResource
from pyopencell.responses.response import Response
from pyopencell.responses.action_status import ActionStatus


class Subscription(BaseResource):
    _name = "subscription"
    _url_path = "/billing/subscription"
    _default_termination_reason = "CC_TERMINATION"

    auditable = {
        "created": None,
        "updated": None,
        "creator": "",
        "updater": "",
    }
    code = ""
    description = ""
    userAccount = ""
    updatedCode = ""
    offerTemplate = ""
    subscriptionDate = None
    terminationDate = None
    endAgreementDate = None
    customFields = []
    terminationReason = ""
    orderNumber = ""
    minimumAmountEl = ""
    minimumAmountElSpark = ""
    minimumLabelEl = ""
    minimumLabelElSpark = ""
    subscribedTillDate = None
    renewed = None
    renewalNotifiedDate = None
    renewalRule = {
        "initialyActiveFor": None,
        "initialyActiveForUnit": "",
        "autoRenew": None,
        "daysNotifyRenewal": None,
        "endOfTermAction": "",
        "terminationReasonCode": "",
        "renewFor": None,
        "renewForUnit": "",
        "extendAgreementPeriodToSubscribedTillDate": None
    }
    billingCycle = "",
    seller = "",
    autoEndOfEngagement = None,
    ratingGroup = ""

    @classmethod
    def get(cls, subscription_code):
        """
        Returns a subscription instance obtained by code.

        :param subscriptionCode:
        :return: Subscription:
        """
        response_data = Client().get(
            cls._url_path,
            subscriptionCode=subscription_code
        )

        status = response_data.get("status")
        if status and status != "SUCCESS":
            return ActionStatus(**response_data)

        return Response(cls, **response_data)

    @classmethod
    def create(cls, **kwargs):
        """
        Creates a subscription instance.

        :param kwargs:
        :return:
        """
        response_data = Client().post(cls._url_path, kwargs)

        return ActionStatus(**response_data)

    def activate(self, services_to_activate):
        """
        Activate services. Subscription should not be in status (RESILIATED OR CANCELLED).

        :param services_to_activate:
        :return:
        """
        action = "activateServices"
        kwargs = {
            "subscription": self.code,
            "servicesToActivate": {
                "service": services_to_activate,
            }
        }
        response_data = Client().post(
            "{}/{}".format(self._url_path, action),
            kwargs)

        return ActionStatus(**response_data)

    def terminate(self, termination_date):
        """
        Terminate OpenCell's Subscription.

        :param termination_date:
        :return:
        """
        response_data = Client().post(
            "{}/{}".format(self._url_path, "terminate"),
            {
                "subscriptionCode": self.code,
                "terminationDate": termination_date,
                "terminationReason": self._default_termination_reason,
            })
        return ActionStatus(**response_data)

    def terminateServices(self, termination_date, services):
        """
        Terminate OpenCell's Subscription services

        :param terminationDate:, services:
        :return:
        """
        response_data = Client().post(
            "{}/{}".format(self._url_path, "terminateServices"),
            {
                "subscriptionCode": self.code,
                "terminationDate": termination_date,
                "services": services,
                "terminationReason": self._default_termination_reason,
            })
        return ActionStatus(**response_data)

    def applyOneShotCharge(
        self, one_shot_charge_code, amountWithoutTax=None,
        description=None, operationDate=None
    ):
        """
        Apply one shot charge to the OpenCell's Subscription.

        :param one_shot_charge_code:
        :return:
        """
        params = {
            "subscription": self.code,
            "oneShotCharge": one_shot_charge_code,
        }
        if amountWithoutTax:
            params['amountWithoutTax'] = amountWithoutTax
        if description:
            params['description'] = description
        if operationDate:
            params['operationDate'] = operationDate
        response_data = Client().post(
            "{}/{}".format(self._url_path, "applyOneShotChargeInstance"),
            params
        )
        return ActionStatus(**response_data)
