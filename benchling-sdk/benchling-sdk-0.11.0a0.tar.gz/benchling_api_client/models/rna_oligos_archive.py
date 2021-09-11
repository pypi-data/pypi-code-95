from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..models.entity_archive_reason import EntityArchiveReason

T = TypeVar("T", bound="RnaOligosArchive")


@attr.s(auto_attribs=True, repr=False)
class RnaOligosArchive:
    """The request body for archiving RNA Oligos."""

    _reason: EntityArchiveReason
    _rna_oligo_ids: List[str]

    def __repr__(self):
        fields = []
        fields.append("reason={}".format(repr(self._reason)))
        fields.append("rna_oligo_ids={}".format(repr(self._rna_oligo_ids)))
        return "RnaOligosArchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        reason = self._reason.value

        rna_oligo_ids = self._rna_oligo_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "reason": reason,
                "rnaOligoIds": rna_oligo_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        reason = EntityArchiveReason(d.pop("reason"))

        rna_oligo_ids = cast(List[str], d.pop("rnaOligoIds"))

        rna_oligos_archive = cls(
            reason=reason,
            rna_oligo_ids=rna_oligo_ids,
        )

        return rna_oligos_archive

    @property
    def reason(self) -> EntityArchiveReason:
        return self._reason

    @reason.setter
    def reason(self, value: EntityArchiveReason) -> None:
        self._reason = value

    @property
    def rna_oligo_ids(self) -> List[str]:
        return self._rna_oligo_ids

    @rna_oligo_ids.setter
    def rna_oligo_ids(self, value: List[str]) -> None:
        self._rna_oligo_ids = value
