from pyopencell.client import Client
from pyopencell.resources.base_resource_list import BaseResourceList
from pyopencell.resources.subscription import Subscription
from pyopencell.responses.paged_response import PagedResponse
from pyopencell.responses.action_status import ActionStatus


class SubscriptionList(BaseResourceList):
    _name = "subscriptions"
    _url_path = "/billing/subscription/list"

    items_resource_class = Subscription
    items_per_page = 10

    subscriptions = []

    @classmethod
    def get(cls, query=None, limit=None, offset=None):
        """
        Returns a Subscription list with subscription instances data.

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
    def get_instances_from_response(self, **response_data):
        if "subscriptions" not in response_data:
            return []

        return response_data["subscriptions"]["subscription"]
