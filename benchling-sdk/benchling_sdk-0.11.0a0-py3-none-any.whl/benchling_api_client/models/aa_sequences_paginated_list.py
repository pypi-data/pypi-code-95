from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.aa_sequence import AaSequence

T = TypeVar("T", bound="AaSequencesPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class AaSequencesPaginatedList:
    """  """

    _aa_sequences: List[AaSequence]
    _next_token: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("aa_sequences={}".format(repr(self._aa_sequences)))
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "AaSequencesPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        aa_sequences = []
        for aa_sequences_item_data in self._aa_sequences:
            aa_sequences_item = aa_sequences_item_data.to_dict()

            aa_sequences.append(aa_sequences_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "aaSequences": aa_sequences,
                "nextToken": next_token,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        aa_sequences = []
        _aa_sequences = d.pop("aaSequences")
        for aa_sequences_item_data in _aa_sequences:
            aa_sequences_item = AaSequence.from_dict(aa_sequences_item_data)

            aa_sequences.append(aa_sequences_item)

        next_token = d.pop("nextToken")

        aa_sequences_paginated_list = cls(
            aa_sequences=aa_sequences,
            next_token=next_token,
        )

        aa_sequences_paginated_list.additional_properties = d
        return aa_sequences_paginated_list

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
    def aa_sequences(self) -> List[AaSequence]:
        return self._aa_sequences

    @aa_sequences.setter
    def aa_sequences(self, value: List[AaSequence]) -> None:
        self._aa_sequences = value

    @property
    def next_token(self) -> str:
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value
