from typing import Any, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="DnaAnnotation")


@attr.s(auto_attribs=True, repr=False)
class DnaAnnotation:
    """  """

    _color: Union[Unset, str] = UNSET
    _end: Union[Unset, int] = UNSET
    _name: Union[Unset, str] = UNSET
    _notes: Union[Unset, str] = UNSET
    _start: Union[Unset, int] = UNSET
    _strand: Union[Unset, int] = UNSET
    _type: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("color={}".format(repr(self._color)))
        fields.append("end={}".format(repr(self._end)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("notes={}".format(repr(self._notes)))
        fields.append("start={}".format(repr(self._start)))
        fields.append("strand={}".format(repr(self._strand)))
        fields.append("type={}".format(repr(self._type)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "DnaAnnotation({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        color = self._color
        end = self._end
        name = self._name
        notes = self._notes
        start = self._start
        strand = self._strand
        type = self._type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if color is not UNSET:
            field_dict["color"] = color
        if end is not UNSET:
            field_dict["end"] = end
        if name is not UNSET:
            field_dict["name"] = name
        if notes is not UNSET:
            field_dict["notes"] = notes
        if start is not UNSET:
            field_dict["start"] = start
        if strand is not UNSET:
            field_dict["strand"] = strand
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        color = d.pop("color", UNSET)

        end = d.pop("end", UNSET)

        name = d.pop("name", UNSET)

        notes = d.pop("notes", UNSET)

        start = d.pop("start", UNSET)

        strand = d.pop("strand", UNSET)

        type = d.pop("type", UNSET)

        dna_annotation = cls(
            color=color,
            end=end,
            name=name,
            notes=notes,
            start=start,
            strand=strand,
            type=type,
        )

        dna_annotation.additional_properties = d
        return dna_annotation

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
    def color(self) -> str:
        if isinstance(self._color, Unset):
            raise NotPresentError(self, "color")
        return self._color

    @color.setter
    def color(self, value: str) -> None:
        self._color = value

    @color.deleter
    def color(self) -> None:
        self._color = UNSET

    @property
    def end(self) -> int:
        if isinstance(self._end, Unset):
            raise NotPresentError(self, "end")
        return self._end

    @end.setter
    def end(self, value: int) -> None:
        self._end = value

    @end.deleter
    def end(self) -> None:
        self._end = UNSET

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
    def notes(self) -> str:
        if isinstance(self._notes, Unset):
            raise NotPresentError(self, "notes")
        return self._notes

    @notes.setter
    def notes(self, value: str) -> None:
        self._notes = value

    @notes.deleter
    def notes(self) -> None:
        self._notes = UNSET

    @property
    def start(self) -> int:
        if isinstance(self._start, Unset):
            raise NotPresentError(self, "start")
        return self._start

    @start.setter
    def start(self, value: int) -> None:
        self._start = value

    @start.deleter
    def start(self) -> None:
        self._start = UNSET

    @property
    def strand(self) -> int:
        if isinstance(self._strand, Unset):
            raise NotPresentError(self, "strand")
        return self._strand

    @strand.setter
    def strand(self, value: int) -> None:
        self._strand = value

    @strand.deleter
    def strand(self) -> None:
        self._strand = UNSET

    @property
    def type(self) -> str:
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: str) -> None:
        self._type = value

    @type.deleter
    def type(self) -> None:
        self._type = UNSET
