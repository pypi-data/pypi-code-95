from typing import Any, cast, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="EntriesUnarchive")


@attr.s(auto_attribs=True, repr=False)
class EntriesUnarchive:
    """  """

    _entry_ids: List[str]

    def __repr__(self):
        fields = []
        fields.append("entry_ids={}".format(repr(self._entry_ids)))
        return "EntriesUnarchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        entry_ids = self._entry_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "entryIds": entry_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        entry_ids = cast(List[str], d.pop("entryIds"))

        entries_unarchive = cls(
            entry_ids=entry_ids,
        )

        return entries_unarchive

    @property
    def entry_ids(self) -> List[str]:
        return self._entry_ids

    @entry_ids.setter
    def entry_ids(self, value: List[str]) -> None:
        self._entry_ids = value
