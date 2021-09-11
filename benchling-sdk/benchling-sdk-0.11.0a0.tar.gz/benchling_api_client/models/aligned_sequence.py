from typing import Any, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="AlignedSequence")


@attr.s(auto_attribs=True, repr=False)
class AlignedSequence:
    """  """

    _bases: Union[Unset, str] = UNSET
    _dna_sequence_id: Union[Unset, str] = UNSET
    _name: Union[Unset, str] = UNSET
    _trim_end: Union[Unset, int] = UNSET
    _trim_start: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("bases={}".format(repr(self._bases)))
        fields.append("dna_sequence_id={}".format(repr(self._dna_sequence_id)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("trim_end={}".format(repr(self._trim_end)))
        fields.append("trim_start={}".format(repr(self._trim_start)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "AlignedSequence({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        bases = self._bases
        dna_sequence_id = self._dna_sequence_id
        name = self._name
        trim_end = self._trim_end
        trim_start = self._trim_start

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if bases is not UNSET:
            field_dict["bases"] = bases
        if dna_sequence_id is not UNSET:
            field_dict["dnaSequenceId"] = dna_sequence_id
        if name is not UNSET:
            field_dict["name"] = name
        if trim_end is not UNSET:
            field_dict["trimEnd"] = trim_end
        if trim_start is not UNSET:
            field_dict["trimStart"] = trim_start

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        bases = d.pop("bases", UNSET)

        dna_sequence_id = d.pop("dnaSequenceId", UNSET)

        name = d.pop("name", UNSET)

        trim_end = d.pop("trimEnd", UNSET)

        trim_start = d.pop("trimStart", UNSET)

        aligned_sequence = cls(
            bases=bases,
            dna_sequence_id=dna_sequence_id,
            name=name,
            trim_end=trim_end,
            trim_start=trim_start,
        )

        aligned_sequence.additional_properties = d
        return aligned_sequence

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
    def bases(self) -> str:
        if isinstance(self._bases, Unset):
            raise NotPresentError(self, "bases")
        return self._bases

    @bases.setter
    def bases(self, value: str) -> None:
        self._bases = value

    @bases.deleter
    def bases(self) -> None:
        self._bases = UNSET

    @property
    def dna_sequence_id(self) -> str:
        if isinstance(self._dna_sequence_id, Unset):
            raise NotPresentError(self, "dna_sequence_id")
        return self._dna_sequence_id

    @dna_sequence_id.setter
    def dna_sequence_id(self, value: str) -> None:
        self._dna_sequence_id = value

    @dna_sequence_id.deleter
    def dna_sequence_id(self) -> None:
        self._dna_sequence_id = UNSET

    @property
    def name(self) -> str:
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @name.deleter
    def name(self) -> None:
        self._name = UNSET

    @property
    def trim_end(self) -> int:
        if isinstance(self._trim_end, Unset):
            raise NotPresentError(self, "trim_end")
        return self._trim_end

    @trim_end.setter
    def trim_end(self, value: int) -> None:
        self._trim_end = value

    @trim_end.deleter
    def trim_end(self) -> None:
        self._trim_end = UNSET

    @property
    def trim_start(self) -> int:
        if isinstance(self._trim_start, Unset):
            raise NotPresentError(self, "trim_start")
        return self._trim_start

    @trim_start.setter
    def trim_start(self, value: int) -> None:
        self._trim_start = value

    @trim_start.deleter
    def trim_start(self) -> None:
        self._trim_start = UNSET
