from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..models.entity_archive_reason import EntityArchiveReason

T = TypeVar("T", bound="AaSequencesArchive")


@attr.s(auto_attribs=True, repr=False)
class AaSequencesArchive:
    """The request body for archiving AA sequences."""

    _aa_sequence_ids: List[str]
    _reason: EntityArchiveReason

    def __repr__(self):
        fields = []
        fields.append("aa_sequence_ids={}".format(repr(self._aa_sequence_ids)))
        fields.append("reason={}".format(repr(self._reason)))
        return "AaSequencesArchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        aa_sequence_ids = self._aa_sequence_ids

        reason = self._reason.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "aaSequenceIds": aa_sequence_ids,
                "reason": reason,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        aa_sequence_ids = cast(List[str], d.pop("aaSequenceIds"))

        reason = EntityArchiveReason(d.pop("reason"))

        aa_sequences_archive = cls(
            aa_sequence_ids=aa_sequence_ids,
            reason=reason,
        )

        return aa_sequences_archive

    @property
    def aa_sequence_ids(self) -> List[str]:
        return self._aa_sequence_ids

    @aa_sequence_ids.setter
    def aa_sequence_ids(self, value: List[str]) -> None:
        self._aa_sequence_ids = value

    @property
    def reason(self) -> EntityArchiveReason:
        return self._reason

    @reason.setter
    def reason(self, value: EntityArchiveReason) -> None:
        self._reason = value
