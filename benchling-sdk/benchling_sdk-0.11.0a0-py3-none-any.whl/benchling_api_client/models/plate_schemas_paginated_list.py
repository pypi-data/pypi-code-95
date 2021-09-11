from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.plate_schema import PlateSchema

T = TypeVar("T", bound="PlateSchemasPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class PlateSchemasPaginatedList:
    """  """

    _next_token: str
    _plate_schemas: List[PlateSchema]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("plate_schemas={}".format(repr(self._plate_schemas)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "PlateSchemasPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        next_token = self._next_token
        plate_schemas = []
        for plate_schemas_item_data in self._plate_schemas:
            plate_schemas_item = plate_schemas_item_data.to_dict()

            plate_schemas.append(plate_schemas_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "nextToken": next_token,
                "plateSchemas": plate_schemas,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        next_token = d.pop("nextToken")

        plate_schemas = []
        _plate_schemas = d.pop("plateSchemas")
        for plate_schemas_item_data in _plate_schemas:
            plate_schemas_item = PlateSchema.from_dict(plate_schemas_item_data)

            plate_schemas.append(plate_schemas_item)

        plate_schemas_paginated_list = cls(
            next_token=next_token,
            plate_schemas=plate_schemas,
        )

        plate_schemas_paginated_list.additional_properties = d
        return plate_schemas_paginated_list

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
    def plate_schemas(self) -> List[PlateSchema]:
        return self._plate_schemas

    @plate_schemas.setter
    def plate_schemas(self, value: List[PlateSchema]) -> None:
        self._plate_schemas = value
