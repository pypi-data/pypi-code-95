from pyopencell.responses.action_status import ActionStatus


class Response:
    action_status = {}

    def __init__(self, cls, **kwargs):
        self.action_status = ActionStatus(**kwargs.get("actionStatus"))

        instance = cls(**kwargs[cls._name])
        setattr(self, cls._name, instance)
