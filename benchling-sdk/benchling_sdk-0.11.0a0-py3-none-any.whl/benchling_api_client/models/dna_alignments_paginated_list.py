from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.dna_alignment_summary import DnaAlignmentSummary

T = TypeVar("T", bound="DnaAlignmentsPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class DnaAlignmentsPaginatedList:
    """  """

    _dna_alignments: List[DnaAlignmentSummary]
    _next_token: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("dna_alignments={}".format(repr(self._dna_alignments)))
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "DnaAlignmentsPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        dna_alignments = []
        for dna_alignments_item_data in self._dna_alignments:
            dna_alignments_item = dna_alignments_item_data.to_dict()

            dna_alignments.append(dna_alignments_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "dnaAlignments": dna_alignments,
                "nextToken": next_token,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        dna_alignments = []
        _dna_alignments = d.pop("dnaAlignments")
        for dna_alignments_item_data in _dna_alignments:
            dna_alignments_item = DnaAlignmentSummary.from_dict(dna_alignments_item_data)

            dna_alignments.append(dna_alignments_item)

        next_token = d.pop("nextToken")

        dna_alignments_paginated_list = cls(
            dna_alignments=dna_alignments,
            next_token=next_token,
        )

        dna_alignments_paginated_list.additional_properties = d
        return dna_alignments_paginated_list

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
    def dna_alignments(self) -> List[DnaAlignmentSummary]:
        return self._dna_alignments

    @dna_alignments.setter
    def dna_alignments(self, value: List[DnaAlignmentSummary]) -> None:
        self._dna_alignments = value

    @property
    def next_token(self) -> str:
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value
