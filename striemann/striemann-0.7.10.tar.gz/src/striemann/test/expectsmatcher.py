"""An expects matcher for asserting metrics are recorded.

https://pypi.python.org/pypi/expects
"""

__all__ = ["contain_metric"]


from expects.matchers import Matcher
from .fakes import metric_id


class contain_metric(Matcher):
    def __init__(self, service_name, tags=[], value=None, **kwargs):
        self.value = value
        self.id = metric_id(service_name, tags, kwargs)

    def _match(self, subject):
        if self.value is not None:
            reason_suffix = " with id {} and value {}".format(self.id, self.value)
        else:
            reason_suffix = " with id {}".format(self.id)

        for id, value in subject:
            if id == self.id and (value == self.value or self.value is None):
                return True, ["metric found" + reason_suffix]

        return False, ["metric not found" + reason_suffix]
