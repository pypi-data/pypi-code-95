from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.request_schema import RequestSchema

T = TypeVar("T", bound="RequestSchemasPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class RequestSchemasPaginatedList:
    """  """

    _next_token: str
    _request_schemas: List[RequestSchema]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("request_schemas={}".format(repr(self._request_schemas)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "RequestSchemasPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        next_token = self._next_token
        request_schemas = []
        for request_schemas_item_data in self._request_schemas:
            request_schemas_item = request_schemas_item_data.to_dict()

            request_schemas.append(request_schemas_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "nextToken": next_token,
                "requestSchemas": request_schemas,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        next_token = d.pop("nextToken")

        request_schemas = []
        _request_schemas = d.pop("requestSchemas")
        for request_schemas_item_data in _request_schemas:
            request_schemas_item = RequestSchema.from_dict(request_schemas_item_data)

            request_schemas.append(request_schemas_item)

        request_schemas_paginated_list = cls(
            next_token=next_token,
            request_schemas=request_schemas,
        )

        request_schemas_paginated_list.additional_properties = d
        return request_schemas_paginated_list

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
    def request_schemas(self) -> List[RequestSchema]:
        return self._request_schemas

    @request_schemas.setter
    def request_schemas(self, value: List[RequestSchema]) -> None:
        self._request_schemas = value
