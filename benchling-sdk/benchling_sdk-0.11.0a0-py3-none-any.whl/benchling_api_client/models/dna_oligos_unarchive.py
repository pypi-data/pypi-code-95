from typing import Any, cast, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="DnaOligosUnarchive")


@attr.s(auto_attribs=True, repr=False)
class DnaOligosUnarchive:
    """The request body for unarchiving DNA Oligos."""

    _dna_oligo_ids: List[str]

    def __repr__(self):
        fields = []
        fields.append("dna_oligo_ids={}".format(repr(self._dna_oligo_ids)))
        return "DnaOligosUnarchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        dna_oligo_ids = self._dna_oligo_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "dnaOligoIds": dna_oligo_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        dna_oligo_ids = cast(List[str], d.pop("dnaOligoIds"))

        dna_oligos_unarchive = cls(
            dna_oligo_ids=dna_oligo_ids,
        )

        return dna_oligos_unarchive

    @property
    def dna_oligo_ids(self) -> List[str]:
        return self._dna_oligo_ids

    @dna_oligo_ids.setter
    def dna_oligo_ids(self, value: List[str]) -> None:
        self._dna_oligo_ids = value
