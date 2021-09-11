from typing import Any, cast, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="CustomEntitiesUnarchive")


@attr.s(auto_attribs=True, repr=False)
class CustomEntitiesUnarchive:
    """The request body for unarchiving custom entities."""

    _custom_entity_ids: List[str]

    def __repr__(self):
        fields = []
        fields.append("custom_entity_ids={}".format(repr(self._custom_entity_ids)))
        return "CustomEntitiesUnarchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        custom_entity_ids = self._custom_entity_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "customEntityIds": custom_entity_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        custom_entity_ids = cast(List[str], d.pop("customEntityIds"))

        custom_entities_unarchive = cls(
            custom_entity_ids=custom_entity_ids,
        )

        return custom_entities_unarchive

    @property
    def custom_entity_ids(self) -> List[str]:
        return self._custom_entity_ids

    @custom_entity_ids.setter
    def custom_entity_ids(self, value: List[str]) -> None:
        self._custom_entity_ids = value
