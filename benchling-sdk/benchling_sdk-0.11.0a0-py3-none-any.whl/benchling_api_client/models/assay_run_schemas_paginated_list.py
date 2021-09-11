from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.assay_run_schema import AssayRunSchema

T = TypeVar("T", bound="AssayRunSchemasPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class AssayRunSchemasPaginatedList:
    """  """

    _assay_run_schemas: List[AssayRunSchema]
    _next_token: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("assay_run_schemas={}".format(repr(self._assay_run_schemas)))
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "AssayRunSchemasPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        assay_run_schemas = []
        for assay_run_schemas_item_data in self._assay_run_schemas:
            assay_run_schemas_item = assay_run_schemas_item_data.to_dict()

            assay_run_schemas.append(assay_run_schemas_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "assayRunSchemas": assay_run_schemas,
                "nextToken": next_token,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        assay_run_schemas = []
        _assay_run_schemas = d.pop("assayRunSchemas")
        for assay_run_schemas_item_data in _assay_run_schemas:
            assay_run_schemas_item = AssayRunSchema.from_dict(assay_run_schemas_item_data)

            assay_run_schemas.append(assay_run_schemas_item)

        next_token = d.pop("nextToken")

        assay_run_schemas_paginated_list = cls(
            assay_run_schemas=assay_run_schemas,
            next_token=next_token,
        )

        assay_run_schemas_paginated_list.additional_properties = d
        return assay_run_schemas_paginated_list

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
    def assay_run_schemas(self) -> List[AssayRunSchema]:
        return self._assay_run_schemas

    @assay_run_schemas.setter
    def assay_run_schemas(self, value: List[AssayRunSchema]) -> None:
        self._assay_run_schemas = value

    @property
    def next_token(self) -> str:
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value
