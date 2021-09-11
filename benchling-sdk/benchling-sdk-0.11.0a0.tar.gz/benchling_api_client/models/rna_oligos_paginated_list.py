from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.rna_oligo import RnaOligo

T = TypeVar("T", bound="RnaOligosPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class RnaOligosPaginatedList:
    """  """

    _rna_oligos: List[RnaOligo]
    _next_token: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("rna_oligos={}".format(repr(self._rna_oligos)))
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "RnaOligosPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        rna_oligos = []
        for rna_oligos_item_data in self._rna_oligos:
            rna_oligos_item = rna_oligos_item_data.to_dict()

            rna_oligos.append(rna_oligos_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "rnaOligos": rna_oligos,
                "nextToken": next_token,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        rna_oligos = []
        _rna_oligos = d.pop("rnaOligos")
        for rna_oligos_item_data in _rna_oligos:
            rna_oligos_item = RnaOligo.from_dict(rna_oligos_item_data)

            rna_oligos.append(rna_oligos_item)

        next_token = d.pop("nextToken")

        rna_oligos_paginated_list = cls(
            rna_oligos=rna_oligos,
            next_token=next_token,
        )

        rna_oligos_paginated_list.additional_properties = d
        return rna_oligos_paginated_list

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
    def rna_oligos(self) -> List[RnaOligo]:
        return self._rna_oligos

    @rna_oligos.setter
    def rna_oligos(self, value: List[RnaOligo]) -> None:
        self._rna_oligos = value

    @property
    def next_token(self) -> str:
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value
