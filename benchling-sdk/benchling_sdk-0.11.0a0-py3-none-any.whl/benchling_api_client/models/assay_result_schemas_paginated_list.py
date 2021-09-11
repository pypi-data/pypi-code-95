from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.assay_result_schema import AssayResultSchema

T = TypeVar("T", bound="AssayResultSchemasPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class AssayResultSchemasPaginatedList:
    """  """

    _assay_result_schemas: List[AssayResultSchema]
    _next_token: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("assay_result_schemas={}".format(repr(self._assay_result_schemas)))
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "AssayResultSchemasPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        assay_result_schemas = []
        for assay_result_schemas_item_data in self._assay_result_schemas:
            assay_result_schemas_item = assay_result_schemas_item_data.to_dict()

            assay_result_schemas.append(assay_result_schemas_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "assayResultSchemas": assay_result_schemas,
                "nextToken": next_token,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        assay_result_schemas = []
        _assay_result_schemas = d.pop("assayResultSchemas")
        for assay_result_schemas_item_data in _assay_result_schemas:
            assay_result_schemas_item = AssayResultSchema.from_dict(assay_result_schemas_item_data)

            assay_result_schemas.append(assay_result_schemas_item)

        next_token = d.pop("nextToken")

        assay_result_schemas_paginated_list = cls(
            assay_result_schemas=assay_result_schemas,
            next_token=next_token,
        )

        assay_result_schemas_paginated_list.additional_properties = d
        return assay_result_schemas_paginated_list

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
    def assay_result_schemas(self) -> List[AssayResultSchema]:
        return self._assay_result_schemas

    @assay_result_schemas.setter
    def assay_result_schemas(self, value: List[AssayResultSchema]) -> None:
        self._assay_result_schemas = value

    @property
    def next_token(self) -> str:
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value
