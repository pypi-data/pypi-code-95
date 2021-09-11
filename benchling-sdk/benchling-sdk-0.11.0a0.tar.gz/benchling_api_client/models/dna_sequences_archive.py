from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..models.entity_archive_reason import EntityArchiveReason

T = TypeVar("T", bound="DnaSequencesArchive")


@attr.s(auto_attribs=True, repr=False)
class DnaSequencesArchive:
    """The request body for archiving DNA sequences."""

    _dna_sequence_ids: List[str]
    _reason: EntityArchiveReason

    def __repr__(self):
        fields = []
        fields.append("dna_sequence_ids={}".format(repr(self._dna_sequence_ids)))
        fields.append("reason={}".format(repr(self._reason)))
        return "DnaSequencesArchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        dna_sequence_ids = self._dna_sequence_ids

        reason = self._reason.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "dnaSequenceIds": dna_sequence_ids,
                "reason": reason,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        dna_sequence_ids = cast(List[str], d.pop("dnaSequenceIds"))

        reason = EntityArchiveReason(d.pop("reason"))

        dna_sequences_archive = cls(
            dna_sequence_ids=dna_sequence_ids,
            reason=reason,
        )

        return dna_sequences_archive

    @property
    def dna_sequence_ids(self) -> List[str]:
        return self._dna_sequence_ids

    @dna_sequence_ids.setter
    def dna_sequence_ids(self, value: List[str]) -> None:
        self._dna_sequence_ids = value

    @property
    def reason(self) -> EntityArchiveReason:
        return self._reason

    @reason.setter
    def reason(self, value: EntityArchiveReason) -> None:
        self._reason = value
