# coding: utf8

__all__ = ["Step"]

from .._forward_curve_types import OptStr
from ..._object_definition import ObjectDefinition


class Step(ObjectDefinition):
    """
    Parameters
    ----------
    effective_date : str, optional

    meeting_date : str, optional

    """

    def __init__(
        self,
        effective_date: OptStr = None,
        meeting_date: OptStr = None,
    ) -> None:
        super().__init__()
        self.effective_date = effective_date
        self.meeting_date = meeting_date

    @property
    def effective_date(self):
        """
        :return: str
        """
        return self._get_parameter("effectiveDate")

    @effective_date.setter
    def effective_date(self, value):
        self._set_parameter("effectiveDate", value)

    @property
    def meeting_date(self):
        """
        :return: str
        """
        return self._get_parameter("meetingDate")

    @meeting_date.setter
    def meeting_date(self, value):
        self._set_parameter("meetingDate", value)
