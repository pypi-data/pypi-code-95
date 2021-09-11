from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.entity_schema import EntitySchema

T = TypeVar("T", bound="EntitySchemasList")


@attr.s(auto_attribs=True, repr=False)
class EntitySchemasList:
    """  """

    _entity_schemas: List[EntitySchema]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("entity_schemas={}".format(repr(self._entity_schemas)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "EntitySchemasList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        entity_schemas = []
        for entity_schemas_item_data in self._entity_schemas:
            entity_schemas_item = entity_schemas_item_data.to_dict()

            entity_schemas.append(entity_schemas_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "entitySchemas": entity_schemas,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        entity_schemas = []
        _entity_schemas = d.pop("entitySchemas")
        for entity_schemas_item_data in _entity_schemas:
            entity_schemas_item = EntitySchema.from_dict(entity_schemas_item_data)

            entity_schemas.append(entity_schemas_item)

        entity_schemas_list = cls(
            entity_schemas=entity_schemas,
        )

        entity_schemas_list.additional_properties = d
        return entity_schemas_list

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
    def entity_schemas(self) -> List[EntitySchema]:
        return self._entity_schemas

    @entity_schemas.setter
    def entity_schemas(self, value: List[EntitySchema]) -> None:
        self._entity_schemas = value
