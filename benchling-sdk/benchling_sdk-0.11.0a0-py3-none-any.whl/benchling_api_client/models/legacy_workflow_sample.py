import datetime
from typing import Any, cast, Dict, List, Optional, Type, TypeVar

import attr
from dateutil.parser import isoparse

T = TypeVar("T", bound="LegacyWorkflowSample")


@attr.s(auto_attribs=True, repr=False)
class LegacyWorkflowSample:
    """  """

    _batch_id: str
    _container_ids: List[str]
    _created_at: datetime.datetime
    _id: str
    _name: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("batch_id={}".format(repr(self._batch_id)))
        fields.append("container_ids={}".format(repr(self._container_ids)))
        fields.append("created_at={}".format(repr(self._created_at)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "LegacyWorkflowSample({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        batch_id = self._batch_id
        container_ids = self._container_ids

        created_at = self._created_at.isoformat()

        id = self._id
        name = self._name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "batchId": batch_id,
                "containerIds": container_ids,
                "createdAt": created_at,
                "id": id,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        batch_id = d.pop("batchId")

        container_ids = cast(List[str], d.pop("containerIds"))

        created_at = isoparse(d.pop("createdAt"))

        id = d.pop("id")

        name = d.pop("name")

        legacy_workflow_sample = cls(
            batch_id=batch_id,
            container_ids=container_ids,
            created_at=created_at,
            id=id,
            name=name,
        )

        legacy_workflow_sample.additional_properties = d
        return legacy_workflow_sample

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
    def batch_id(self) -> str:
        return self._batch_id

    @batch_id.setter
    def batch_id(self, value: str) -> None:
        self._batch_id = value

    @property
    def container_ids(self) -> List[str]:
        return self._container_ids

    @container_ids.setter
    def container_ids(self, value: List[str]) -> None:
        self._container_ids = value

    @property
    def created_at(self) -> datetime.datetime:
        return self._created_at

    @created_at.setter
    def created_at(self, value: datetime.datetime) -> None:
        self._created_at = value

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value
