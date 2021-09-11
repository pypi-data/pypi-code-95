from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.box_schema import BoxSchema

T = TypeVar("T", bound="BoxSchemasList")


@attr.s(auto_attribs=True, repr=False)
class BoxSchemasList:
    """  """

    _box_schemas: List[BoxSchema]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("box_schemas={}".format(repr(self._box_schemas)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "BoxSchemasList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        box_schemas = []
        for box_schemas_item_data in self._box_schemas:
            box_schemas_item = box_schemas_item_data.to_dict()

            box_schemas.append(box_schemas_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "boxSchemas": box_schemas,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        box_schemas = []
        _box_schemas = d.pop("boxSchemas")
        for box_schemas_item_data in _box_schemas:
            box_schemas_item = BoxSchema.from_dict(box_schemas_item_data)

            box_schemas.append(box_schemas_item)

        box_schemas_list = cls(
            box_schemas=box_schemas,
        )

        box_schemas_list.additional_properties = d
        return box_schemas_list

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
    def box_schemas(self) -> List[BoxSchema]:
        return self._box_schemas

    @box_schemas.setter
    def box_schemas(self, value: List[BoxSchema]) -> None:
        self._box_schemas = value
