from typing import Any, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.archive_record import ArchiveRecord
from ..models.dropdown_field_definition import DropdownFieldDefinition
from ..models.entity_schema_constraint import EntitySchemaConstraint
from ..models.entity_schema_containable_type import EntitySchemaContainableType
from ..models.float_field_definition import FloatFieldDefinition
from ..models.integer_field_definition import IntegerFieldDefinition
from ..models.schema_link_field_definition import SchemaLinkFieldDefinition
from ..models.simple_field_definition import SimpleFieldDefinition
from ..types import UNSET, Unset

T = TypeVar("T", bound="EntitySchema")


@attr.s(auto_attribs=True, repr=False)
class EntitySchema:
    """  """

    _field_definitions: List[
        Union[
            SimpleFieldDefinition,
            IntegerFieldDefinition,
            FloatFieldDefinition,
            DropdownFieldDefinition,
            SchemaLinkFieldDefinition,
        ]
    ]
    _id: str
    _name: str
    _type: str
    _constraint: Union[Unset, None, EntitySchemaConstraint] = UNSET
    _containable_type: Union[Unset, EntitySchemaContainableType] = UNSET
    _prefix: Union[Unset, str] = UNSET
    _registry_id: Union[Unset, str] = UNSET
    _archive_record: Union[Unset, None, ArchiveRecord] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("field_definitions={}".format(repr(self._field_definitions)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("type={}".format(repr(self._type)))
        fields.append("constraint={}".format(repr(self._constraint)))
        fields.append("containable_type={}".format(repr(self._containable_type)))
        fields.append("prefix={}".format(repr(self._prefix)))
        fields.append("registry_id={}".format(repr(self._registry_id)))
        fields.append("archive_record={}".format(repr(self._archive_record)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "EntitySchema({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        field_definitions = []
        for field_definitions_item_data in self._field_definitions:
            if isinstance(field_definitions_item_data, SimpleFieldDefinition):
                field_definitions_item = field_definitions_item_data.to_dict()

            elif isinstance(field_definitions_item_data, IntegerFieldDefinition):
                field_definitions_item = field_definitions_item_data.to_dict()

            elif isinstance(field_definitions_item_data, FloatFieldDefinition):
                field_definitions_item = field_definitions_item_data.to_dict()

            elif isinstance(field_definitions_item_data, DropdownFieldDefinition):
                field_definitions_item = field_definitions_item_data.to_dict()

            else:
                field_definitions_item = field_definitions_item_data.to_dict()

            field_definitions.append(field_definitions_item)

        id = self._id
        name = self._name
        type = self._type
        constraint: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._constraint, Unset):
            constraint = self._constraint.to_dict() if self._constraint else None

        containable_type: Union[Unset, int] = UNSET
        if not isinstance(self._containable_type, Unset):
            containable_type = self._containable_type.value

        prefix = self._prefix
        registry_id = self._registry_id
        archive_record: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._archive_record, Unset):
            archive_record = self._archive_record.to_dict() if self._archive_record else None

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fieldDefinitions": field_definitions,
                "id": id,
                "name": name,
                "type": type,
            }
        )
        if constraint is not UNSET:
            field_dict["constraint"] = constraint
        if containable_type is not UNSET:
            field_dict["containableType"] = containable_type
        if prefix is not UNSET:
            field_dict["prefix"] = prefix
        if registry_id is not UNSET:
            field_dict["registryId"] = registry_id
        if archive_record is not UNSET:
            field_dict["archiveRecord"] = archive_record

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        field_definitions = []
        _field_definitions = d.pop("fieldDefinitions")
        for field_definitions_item_data in _field_definitions:

            def _parse_field_definitions_item(
                data: Union[Dict[str, Any]]
            ) -> Union[
                SimpleFieldDefinition,
                IntegerFieldDefinition,
                FloatFieldDefinition,
                DropdownFieldDefinition,
                SchemaLinkFieldDefinition,
            ]:
                field_definitions_item: Union[
                    SimpleFieldDefinition,
                    IntegerFieldDefinition,
                    FloatFieldDefinition,
                    DropdownFieldDefinition,
                    SchemaLinkFieldDefinition,
                ]
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    field_definitions_item = SimpleFieldDefinition.from_dict(data)

                    return field_definitions_item
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    field_definitions_item = IntegerFieldDefinition.from_dict(data)

                    return field_definitions_item
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    field_definitions_item = FloatFieldDefinition.from_dict(data)

                    return field_definitions_item
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    field_definitions_item = DropdownFieldDefinition.from_dict(data)

                    return field_definitions_item
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                field_definitions_item = SchemaLinkFieldDefinition.from_dict(data)

                return field_definitions_item

            field_definitions_item = _parse_field_definitions_item(field_definitions_item_data)

            field_definitions.append(field_definitions_item)

        id = d.pop("id")

        name = d.pop("name")

        type = d.pop("type")

        constraint = None
        _constraint = d.pop("constraint", UNSET)
        if _constraint is not None and not isinstance(_constraint, Unset):
            constraint = EntitySchemaConstraint.from_dict(_constraint)

        containable_type = None
        _containable_type = d.pop("containableType", UNSET)
        if _containable_type is not None and _containable_type is not UNSET:
            containable_type = EntitySchemaContainableType(_containable_type)

        prefix = d.pop("prefix", UNSET)

        registry_id = d.pop("registryId", UNSET)

        archive_record = None
        _archive_record = d.pop("archiveRecord", UNSET)
        if _archive_record is not None and not isinstance(_archive_record, Unset):
            archive_record = ArchiveRecord.from_dict(_archive_record)

        entity_schema = cls(
            field_definitions=field_definitions,
            id=id,
            name=name,
            type=type,
            constraint=constraint,
            containable_type=containable_type,
            prefix=prefix,
            registry_id=registry_id,
            archive_record=archive_record,
        )

        entity_schema.additional_properties = d
        return entity_schema

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
    def field_definitions(
        self,
    ) -> List[
        Union[
            SimpleFieldDefinition,
            IntegerFieldDefinition,
            FloatFieldDefinition,
            DropdownFieldDefinition,
            SchemaLinkFieldDefinition,
        ]
    ]:
        return self._field_definitions

    @field_definitions.setter
    def field_definitions(
        self,
        value: List[
            Union[
                SimpleFieldDefinition,
                IntegerFieldDefinition,
                FloatFieldDefinition,
                DropdownFieldDefinition,
                SchemaLinkFieldDefinition,
            ]
        ],
    ) -> None:
        self._field_definitions = value

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, value: str) -> None:
        self._type = value

    @property
    def constraint(self) -> Optional[EntitySchemaConstraint]:
        if isinstance(self._constraint, Unset):
            raise NotPresentError(self, "constraint")
        return self._constraint

    @constraint.setter
    def constraint(self, value: Optional[EntitySchemaConstraint]) -> None:
        self._constraint = value

    @constraint.deleter
    def constraint(self) -> None:
        self._constraint = UNSET

    @property
    def containable_type(self) -> EntitySchemaContainableType:
        if isinstance(self._containable_type, Unset):
            raise NotPresentError(self, "containable_type")
        return self._containable_type

    @containable_type.setter
    def containable_type(self, value: EntitySchemaContainableType) -> None:
        self._containable_type = value

    @containable_type.deleter
    def containable_type(self) -> None:
        self._containable_type = UNSET

    @property
    def prefix(self) -> str:
        if isinstance(self._prefix, Unset):
            raise NotPresentError(self, "prefix")
        return self._prefix

    @prefix.setter
    def prefix(self, value: str) -> None:
        self._prefix = value

    @prefix.deleter
    def prefix(self) -> None:
        self._prefix = UNSET

    @property
    def registry_id(self) -> str:
        if isinstance(self._registry_id, Unset):
            raise NotPresentError(self, "registry_id")
        return self._registry_id

    @registry_id.setter
    def registry_id(self, value: str) -> None:
        self._registry_id = value

    @registry_id.deleter
    def registry_id(self) -> None:
        self._registry_id = UNSET

    @property
    def archive_record(self) -> Optional[ArchiveRecord]:
        if isinstance(self._archive_record, Unset):
            raise NotPresentError(self, "archive_record")
        return self._archive_record

    @archive_record.setter
    def archive_record(self, value: Optional[ArchiveRecord]) -> None:
        self._archive_record = value

    @archive_record.deleter
    def archive_record(self) -> None:
        self._archive_record = UNSET
