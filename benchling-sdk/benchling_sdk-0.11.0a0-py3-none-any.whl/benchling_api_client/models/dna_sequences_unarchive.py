from typing import Any, cast, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="DnaSequencesUnarchive")


@attr.s(auto_attribs=True, repr=False)
class DnaSequencesUnarchive:
    """The request body for unarchiving DNA sequences."""

    _dna_sequence_ids: List[str]

    def __repr__(self):
        fields = []
        fields.append("dna_sequence_ids={}".format(repr(self._dna_sequence_ids)))
        return "DnaSequencesUnarchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        dna_sequence_ids = self._dna_sequence_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "dnaSequenceIds": dna_sequence_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        dna_sequence_ids = cast(List[str], d.pop("dnaSequenceIds"))

        dna_sequences_unarchive = cls(
            dna_sequence_ids=dna_sequence_ids,
        )

        return dna_sequences_unarchive

    @property
    def dna_sequence_ids(self) -> List[str]:
        return self._dna_sequence_ids

    @dna_sequence_ids.setter
    def dna_sequence_ids(self, value: List[str]) -> None:
        self._dna_sequence_ids = value
