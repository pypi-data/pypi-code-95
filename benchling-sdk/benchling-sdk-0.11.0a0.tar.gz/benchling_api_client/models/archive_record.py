from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

T = TypeVar("T", bound="ArchiveRecord")


@attr.s(auto_attribs=True, repr=False)
class ArchiveRecord:
    """  """

    _reason: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("reason={}".format(repr(self._reason)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "ArchiveRecord({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        reason = self._reason

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "reason": reason,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        reason = d.pop("reason")

        archive_record = cls(
            reason=reason,
        )

        archive_record.additional_properties = d
        return archive_record

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
    def reason(self) -> str:
        return self._reason

    @reason.setter
    def reason(self, value: str) -> None:
        self._reason = value
