from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.sample_group_status import SampleGroupStatus

T = TypeVar("T", bound="SampleGroupStatusUpdate")


@attr.s(auto_attribs=True, repr=False)
class SampleGroupStatusUpdate:
    """  """

    _sample_group_id: str
    _status: SampleGroupStatus
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("sample_group_id={}".format(repr(self._sample_group_id)))
        fields.append("status={}".format(repr(self._status)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "SampleGroupStatusUpdate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        sample_group_id = self._sample_group_id
        status = self._status.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "sampleGroupId": sample_group_id,
                "status": status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        sample_group_id = d.pop("sampleGroupId")

        status = SampleGroupStatus(d.pop("status"))

        sample_group_status_update = cls(
            sample_group_id=sample_group_id,
            status=status,
        )

        sample_group_status_update.additional_properties = d
        return sample_group_status_update

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
    def sample_group_id(self) -> str:
        return self._sample_group_id

    @sample_group_id.setter
    def sample_group_id(self, value: str) -> None:
        self._sample_group_id = value

    @property
    def status(self) -> SampleGroupStatus:
        return self._status

    @status.setter
    def status(self, value: SampleGroupStatus) -> None:
        self._status = value
