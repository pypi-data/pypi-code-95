from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.request_fulfillment import RequestFulfillment

T = TypeVar("T", bound="RequestFulfillmentsPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class RequestFulfillmentsPaginatedList:
    """ An object containing an array of RequestFulfillments """

    _next_token: str
    _request_fulfillments: List[RequestFulfillment]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("request_fulfillments={}".format(repr(self._request_fulfillments)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "RequestFulfillmentsPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        next_token = self._next_token
        request_fulfillments = []
        for request_fulfillments_item_data in self._request_fulfillments:
            request_fulfillments_item = request_fulfillments_item_data.to_dict()

            request_fulfillments.append(request_fulfillments_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "nextToken": next_token,
                "requestFulfillments": request_fulfillments,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        next_token = d.pop("nextToken")

        request_fulfillments = []
        _request_fulfillments = d.pop("requestFulfillments")
        for request_fulfillments_item_data in _request_fulfillments:
            request_fulfillments_item = RequestFulfillment.from_dict(request_fulfillments_item_data)

            request_fulfillments.append(request_fulfillments_item)

        request_fulfillments_paginated_list = cls(
            next_token=next_token,
            request_fulfillments=request_fulfillments,
        )

        request_fulfillments_paginated_list.additional_properties = d
        return request_fulfillments_paginated_list

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
    def request_fulfillments(self) -> List[RequestFulfillment]:
        return self._request_fulfillments

    @request_fulfillments.setter
    def request_fulfillments(self, value: List[RequestFulfillment]) -> None:
        self._request_fulfillments = value
