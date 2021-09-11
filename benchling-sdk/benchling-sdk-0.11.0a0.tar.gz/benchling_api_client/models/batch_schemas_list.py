from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.batch_schema import BatchSchema

T = TypeVar("T", bound="BatchSchemasList")


@attr.s(auto_attribs=True, repr=False)
class BatchSchemasList:
    """  """

    _batch_schemas: List[BatchSchema]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("batch_schemas={}".format(repr(self._batch_schemas)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "BatchSchemasList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        batch_schemas = []
        for batch_schemas_item_data in self._batch_schemas:
            batch_schemas_item = batch_schemas_item_data.to_dict()

            batch_schemas.append(batch_schemas_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "batchSchemas": batch_schemas,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        batch_schemas = []
        _batch_schemas = d.pop("batchSchemas")
        for batch_schemas_item_data in _batch_schemas:
            batch_schemas_item = BatchSchema.from_dict(batch_schemas_item_data)

            batch_schemas.append(batch_schemas_item)

        batch_schemas_list = cls(
            batch_schemas=batch_schemas,
        )

        batch_schemas_list.additional_properties = d
        return batch_schemas_list

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
    def batch_schemas(self) -> List[BatchSchema]:
        return self._batch_schemas

    @batch_schemas.setter
    def batch_schemas(self, value: List[BatchSchema]) -> None:
        self._batch_schemas = value
