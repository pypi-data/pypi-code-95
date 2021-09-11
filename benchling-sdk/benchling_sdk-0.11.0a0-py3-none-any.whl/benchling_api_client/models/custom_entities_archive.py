from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..models.entity_archive_reason import EntityArchiveReason

T = TypeVar("T", bound="CustomEntitiesArchive")


@attr.s(auto_attribs=True, repr=False)
class CustomEntitiesArchive:
    """The request body for archiving custom entities."""

    _custom_entity_ids: List[str]
    _reason: EntityArchiveReason

    def __repr__(self):
        fields = []
        fields.append("custom_entity_ids={}".format(repr(self._custom_entity_ids)))
        fields.append("reason={}".format(repr(self._reason)))
        return "CustomEntitiesArchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        custom_entity_ids = self._custom_entity_ids

        reason = self._reason.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "customEntityIds": custom_entity_ids,
                "reason": reason,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        custom_entity_ids = cast(List[str], d.pop("customEntityIds"))

        reason = EntityArchiveReason(d.pop("reason"))

        custom_entities_archive = cls(
            custom_entity_ids=custom_entity_ids,
            reason=reason,
        )

        return custom_entities_archive

    @property
    def custom_entity_ids(self) -> List[str]:
        return self._custom_entity_ids

    @custom_entity_ids.setter
    def custom_entity_ids(self, value: List[str]) -> None:
        self._custom_entity_ids = value

    @property
    def reason(self) -> EntityArchiveReason:
        return self._reason

    @reason.setter
    def reason(self, value: EntityArchiveReason) -> None:
        self._reason = value
