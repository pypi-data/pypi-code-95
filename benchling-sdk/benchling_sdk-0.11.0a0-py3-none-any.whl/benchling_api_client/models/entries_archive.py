from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..models.entries_archive_reason import EntriesArchiveReason

T = TypeVar("T", bound="EntriesArchive")


@attr.s(auto_attribs=True, repr=False)
class EntriesArchive:
    """  """

    _entry_ids: List[str]
    _reason: EntriesArchiveReason

    def __repr__(self):
        fields = []
        fields.append("entry_ids={}".format(repr(self._entry_ids)))
        fields.append("reason={}".format(repr(self._reason)))
        return "EntriesArchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        entry_ids = self._entry_ids

        reason = self._reason.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "entryIds": entry_ids,
                "reason": reason,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        entry_ids = cast(List[str], d.pop("entryIds"))

        reason = EntriesArchiveReason(d.pop("reason"))

        entries_archive = cls(
            entry_ids=entry_ids,
            reason=reason,
        )

        return entries_archive

    @property
    def entry_ids(self) -> List[str]:
        return self._entry_ids

    @entry_ids.setter
    def entry_ids(self, value: List[str]) -> None:
        self._entry_ids = value

    @property
    def reason(self) -> EntriesArchiveReason:
        return self._reason

    @reason.setter
    def reason(self, value: EntriesArchiveReason) -> None:
        self._reason = value
