from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.dna_oligo import DnaOligo

T = TypeVar("T", bound="DnaOligosPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class DnaOligosPaginatedList:
    """  """

    _dna_oligos: List[DnaOligo]
    _next_token: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("dna_oligos={}".format(repr(self._dna_oligos)))
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "DnaOligosPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        dna_oligos = []
        for dna_oligos_item_data in self._dna_oligos:
            dna_oligos_item = dna_oligos_item_data.to_dict()

            dna_oligos.append(dna_oligos_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "dnaOligos": dna_oligos,
                "nextToken": next_token,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        dna_oligos = []
        _dna_oligos = d.pop("dnaOligos")
        for dna_oligos_item_data in _dna_oligos:
            dna_oligos_item = DnaOligo.from_dict(dna_oligos_item_data)

            dna_oligos.append(dna_oligos_item)

        next_token = d.pop("nextToken")

        dna_oligos_paginated_list = cls(
            dna_oligos=dna_oligos,
            next_token=next_token,
        )

        dna_oligos_paginated_list.additional_properties = d
        return dna_oligos_paginated_list

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
    def dna_oligos(self) -> List[DnaOligo]:
        return self._dna_oligos

    @dna_oligos.setter
    def dna_oligos(self, value: List[DnaOligo]) -> None:
        self._dna_oligos = value

    @property
    def next_token(self) -> str:
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value
