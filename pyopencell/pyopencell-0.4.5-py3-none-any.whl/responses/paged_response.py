from pyopencell.responses.action_status import ActionStatus
from pyopencell.responses.paging import Paging


class PagedResponse():
    paging = {}
    action_status = {}

    def __init__(self, cls, **response_data):
        self.paging = Paging(**response_data.get("paging"))
        self.action_status = ActionStatus(**response_data.get("actionStatus"))

        instances = []

        instances_from_response = cls.get_instances_from_response(**response_data)

        for instance in instances_from_response:
            instances.append(cls.items_resource_class(**instance))

        setattr(self, cls._name, instances)
