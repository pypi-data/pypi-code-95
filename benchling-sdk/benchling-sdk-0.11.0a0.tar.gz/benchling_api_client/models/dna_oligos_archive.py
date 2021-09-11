from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..models.entity_archive_reason import EntityArchiveReason

T = TypeVar("T", bound="DnaOligosArchive")


@attr.s(auto_attribs=True, repr=False)
class DnaOligosArchive:
    """The request body for archiving DNA Oligos."""

    _dna_oligo_ids: List[str]
    _reason: EntityArchiveReason

    def __repr__(self):
        fields = []
        fields.append("dna_oligo_ids={}".format(repr(self._dna_oligo_ids)))
        fields.append("reason={}".format(repr(self._reason)))
        return "DnaOligosArchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        dna_oligo_ids = self._dna_oligo_ids

        reason = self._reason.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "dnaOligoIds": dna_oligo_ids,
                "reason": reason,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        dna_oligo_ids = cast(List[str], d.pop("dnaOligoIds"))

        reason = EntityArchiveReason(d.pop("reason"))

        dna_oligos_archive = cls(
            dna_oligo_ids=dna_oligo_ids,
            reason=reason,
        )

        return dna_oligos_archive

    @property
    def dna_oligo_ids(self) -> List[str]:
        return self._dna_oligo_ids

    @dna_oligo_ids.setter
    def dna_oligo_ids(self, value: List[str]) -> None:
        self._dna_oligo_ids = value

    @property
    def reason(self) -> EntityArchiveReason:
        return self._reason

    @reason.setter
    def reason(self, value: EntityArchiveReason) -> None:
        self._reason = value
