from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.entry_schema_detailed import EntrySchemaDetailed

T = TypeVar("T", bound="EntrySchemasPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class EntrySchemasPaginatedList:
    """  """

    _entry_schemas: List[EntrySchemaDetailed]
    _next_token: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("entry_schemas={}".format(repr(self._entry_schemas)))
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "EntrySchemasPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        entry_schemas = []
        for entry_schemas_item_data in self._entry_schemas:
            entry_schemas_item = entry_schemas_item_data.to_dict()

            entry_schemas.append(entry_schemas_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "entrySchemas": entry_schemas,
                "nextToken": next_token,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        entry_schemas = []
        _entry_schemas = d.pop("entrySchemas")
        for entry_schemas_item_data in _entry_schemas:
            entry_schemas_item = EntrySchemaDetailed.from_dict(entry_schemas_item_data)

            entry_schemas.append(entry_schemas_item)

        next_token = d.pop("nextToken")

        entry_schemas_paginated_list = cls(
            entry_schemas=entry_schemas,
            next_token=next_token,
        )

        entry_schemas_paginated_list.additional_properties = d
        return entry_schemas_paginated_list

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
    def entry_schemas(self) -> List[EntrySchemaDetailed]:
        return self._entry_schemas

    @entry_schemas.setter
    def entry_schemas(self, value: List[EntrySchemaDetailed]) -> None:
        self._entry_schemas = value

    @property
    def next_token(self) -> str:
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value
