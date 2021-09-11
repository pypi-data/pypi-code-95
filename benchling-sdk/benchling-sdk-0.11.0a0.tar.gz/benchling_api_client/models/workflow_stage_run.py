import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar

import attr
from dateutil.parser import isoparse

from ..models.workflow_stage_run_status import WorkflowStageRunStatus

T = TypeVar("T", bound="WorkflowStageRun")


@attr.s(auto_attribs=True, repr=False)
class WorkflowStageRun:
    """  """

    _created_at: datetime.datetime
    _id: str
    _name: str
    _status: WorkflowStageRunStatus
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("created_at={}".format(repr(self._created_at)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("status={}".format(repr(self._status)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowStageRun({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        created_at = self._created_at.isoformat()

        id = self._id
        name = self._name
        status = self._status.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "createdAt": created_at,
                "id": id,
                "name": name,
                "status": status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        created_at = isoparse(d.pop("createdAt"))

        id = d.pop("id")

        name = d.pop("name")

        status = WorkflowStageRunStatus(d.pop("status"))

        workflow_stage_run = cls(
            created_at=created_at,
            id=id,
            name=name,
            status=status,
        )

        workflow_stage_run.additional_properties = d
        return workflow_stage_run

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

    @property
    def status(self) -> WorkflowStageRunStatus:
        return self._status

    @status.setter
    def status(self, value: WorkflowStageRunStatus) -> None:
        self._status = value
