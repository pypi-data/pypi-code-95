from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.request import Request

T = TypeVar("T", bound="RequestsPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class RequestsPaginatedList:
    """  """

    _next_token: str
    _requests: List[Request]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("requests={}".format(repr(self._requests)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "RequestsPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        next_token = self._next_token
        requests = []
        for requests_item_data in self._requests:
            requests_item = requests_item_data.to_dict()

            requests.append(requests_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "nextToken": next_token,
                "requests": requests,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        next_token = d.pop("nextToken")

        requests = []
        _requests = d.pop("requests")
        for requests_item_data in _requests:
            requests_item = Request.from_dict(requests_item_data)

            requests.append(requests_item)

        requests_paginated_list = cls(
            next_token=next_token,
            requests=requests,
        )

        requests_paginated_list.additional_properties = d
        return requests_paginated_list

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
    def next_token(self) -> str:
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value

    @property
    def requests(self) -> List[Request]:
        return self._requests

    @requests.setter
    def requests(self, value: List[Request]) -> None:
        self._requests = value
