from pyopencell.client import Client
from pyopencell.resources.base_resource import BaseResource
from pyopencell.responses.response import Response
from pyopencell.responses.action_status import ActionStatus


class Access(BaseResource):
    _name = "access"
    _url_path = "/account/access"

    code = ""
    subscription = ""
    startDate = ""
    endDate = ""
    customFields = []
    disabled = False

    @classmethod
    def get(cls, accessCode=None, subscriptionCode=None):
        """
        Returns an access instance obtained by code or by subscription code.

        :param accessCode:
        :param subscriptionCode:
        :return: Access:
        """
        # Only one is required. If the two arguments are missing, a error was returned by the API
        query_params = {}
        if accessCode:
            query_params['accessCode'] = accessCode
        if subscriptionCode:
            query_params['subscriptionCode'] = subscriptionCode
        response_data = Client().get(cls._url_path, **query_params)

        status = response_data.get("status")
        if status and status != "SUCCESS":
            return ActionStatus(**response_data)

        return Response(cls, **response_data)

    @classmethod
    def create(cls, **kwargs):
        """
        Creates an access instance.

        :param kwargs:
        :return:
        """
        response_data = Client().post(cls._url_path, kwargs)

        return ActionStatus(**response_data)
