import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..models.checkout_record_status import CheckoutRecordStatus
from ..models.team_summary import TeamSummary
from ..models.user_summary import UserSummary
from ..types import UNSET, Unset

T = TypeVar("T", bound="CheckoutRecord")


@attr.s(auto_attribs=True, repr=False)
class CheckoutRecord:
    """
    *assignee field* is set if status is "RESERVED" or "CHECKED_OUT", or null if status is "AVAILABLE".

    *comment field* is set when container was last reserved, checked out, or checked into.

    *modifiedAt field* is the date and time when container was last checked out, checked in, or reserved
    """

    _comment: str
    _modified_at: datetime.datetime
    _status: CheckoutRecordStatus
    _assignee: Union[None, UserSummary, TeamSummary]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("comment={}".format(repr(self._comment)))
        fields.append("modified_at={}".format(repr(self._modified_at)))
        fields.append("status={}".format(repr(self._status)))
        fields.append("assignee={}".format(repr(self._assignee)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "CheckoutRecord({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        comment = self._comment
        modified_at = self._modified_at.isoformat()

        status = self._status.value

        assignee: Union[None, Dict[str, Any]]
        if isinstance(self._assignee, Unset):
            assignee = UNSET
        if self._assignee is None:
            assignee = None
        elif isinstance(self._assignee, UserSummary):
            assignee = self._assignee.to_dict()

        else:
            assignee = self._assignee.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "comment": comment,
                "modifiedAt": modified_at,
                "status": status,
                "assignee": assignee,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        comment = d.pop("comment")

        modified_at = isoparse(d.pop("modifiedAt"))

        status = CheckoutRecordStatus(d.pop("status"))

        def _parse_assignee(data: Union[None, Dict[str, Any]]) -> Union[None, UserSummary, TeamSummary]:
            assignee: Union[None, UserSummary, TeamSummary]
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                assignee = UserSummary.from_dict(data)

                return assignee
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            assignee = TeamSummary.from_dict(data)

            return assignee

        assignee = _parse_assignee(d.pop("assignee"))

        checkout_record = cls(
            comment=comment,
            modified_at=modified_at,
            status=status,
            assignee=assignee,
        )

        checkout_record.additional_properties = d
        return checkout_record

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

    def get(self, key, default=None) -> Optional[Any]:
        return self.additional_properties.get(key, default)

    @property
    def comment(self) -> str:
        return self._comment

    @comment.setter
    def comment(self, value: str) -> None:
        self._comment = value

    @property
    def modified_at(self) -> datetime.datetime:
        return self._modified_at

    @modified_at.setter
    def modified_at(self, value: datetime.datetime) -> None:
        self._modified_at = value

    @property
    def status(self) -> CheckoutRecordStatus:
        return self._status

    @status.setter
    def status(self, value: CheckoutRecordStatus) -> None:
        self._status = value

    @property
    def assignee(self) -> Optional[Union[UserSummary, TeamSummary]]:
        return self._assignee

    @assignee.setter
    def assignee(self, value: Optional[Union[UserSummary, TeamSummary]]) -> None:
        self._assignee = value
