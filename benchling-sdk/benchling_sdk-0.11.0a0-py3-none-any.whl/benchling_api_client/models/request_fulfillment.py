import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar

import attr
from dateutil.parser import isoparse

from ..models.sample_group import SampleGroup
from ..models.sample_group_status import SampleGroupStatus

T = TypeVar("T", bound="RequestFulfillment")


@attr.s(auto_attribs=True, repr=False)
class RequestFulfillment:
    """A request fulfillment represents work that is done which changes the status of a request or a sample group within that request.
    Fulfillments are created when state changes between IN_PROGRESS, COMPLETED, or FAILED statuses. Fulfillments do not capture a PENDING state because all requests or request sample groups are considered PENDING until the first corresponding fulfillment is created.
    """

    _created_at: datetime.datetime
    _entry_id: str
    _id: str
    _request_id: str
    _status: SampleGroupStatus
    _sample_group: Optional[SampleGroup]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("created_at={}".format(repr(self._created_at)))
        fields.append("entry_id={}".format(repr(self._entry_id)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("request_id={}".format(repr(self._request_id)))
        fields.append("status={}".format(repr(self._status)))
        fields.append("sample_group={}".format(repr(self._sample_group)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "RequestFulfillment({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        created_at = self._created_at.isoformat()

        entry_id = self._entry_id
        id = self._id
        request_id = self._request_id
        status = self._status.value

        sample_group = self._sample_group.to_dict() if self._sample_group else None

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "createdAt": created_at,
                "entryId": entry_id,
                "id": id,
                "requestId": request_id,
                "status": status,
                "sampleGroup": sample_group,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        created_at = isoparse(d.pop("createdAt"))

        entry_id = d.pop("entryId")

        id = d.pop("id")

        request_id = d.pop("requestId")

        status = SampleGroupStatus(d.pop("status"))

        sample_group = None
        _sample_group = d.pop("sampleGroup")
        if _sample_group is not None:
            sample_group = SampleGroup.from_dict(_sample_group)

        request_fulfillment = cls(
            created_at=created_at,
            entry_id=entry_id,
            id=id,
            request_id=request_id,
            status=status,
            sample_group=sample_group,
        )

        request_fulfillment.additional_properties = d
        return request_fulfillment

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
    def created_at(self) -> datetime.datetime:
        return self._created_at

    @created_at.setter
    def created_at(self, value: datetime.datetime) -> None:
        self._created_at = value

    @property
    def entry_id(self) -> str:
        return self._entry_id

    @entry_id.setter
    def entry_id(self, value: str) -> None:
        self._entry_id = value

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @property
    def request_id(self) -> str:
        return self._request_id

    @request_id.setter
    def request_id(self, value: str) -> None:
        self._request_id = value

    @property
    def status(self) -> SampleGroupStatus:
        return self._status

    @status.setter
    def status(self, value: SampleGroupStatus) -> None:
        self._status = value

    @property
    def sample_group(self) -> Optional[SampleGroup]:
        return self._sample_group

    @sample_group.setter
    def sample_group(self, value: Optional[SampleGroup]) -> None:
        self._sample_group = value
