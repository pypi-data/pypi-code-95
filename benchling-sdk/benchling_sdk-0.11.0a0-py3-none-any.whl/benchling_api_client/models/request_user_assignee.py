from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.user_summary import UserSummary

T = TypeVar("T", bound="RequestUserAssignee")


@attr.s(auto_attribs=True, repr=False)
class RequestUserAssignee:
    """  """

    _user: UserSummary
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("user={}".format(repr(self._user)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "RequestUserAssignee({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        user = self._user.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "user": user,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        user = UserSummary.from_dict(d.pop("user"))

        request_user_assignee = cls(
            user=user,
        )

        request_user_assignee.additional_properties = d
        return request_user_assignee

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
    def user(self) -> UserSummary:
        return self._user

    @user.setter
    def user(self, value: UserSummary) -> None:
        self._user = value
