import datetime
from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..extensions import NotPresentError
from ..models.fields import Fields
from ..models.request_sample_group_create import RequestSampleGroupCreate
from ..models.request_write_team_assignee import RequestWriteTeamAssignee
from ..models.request_write_user_assignee import RequestWriteUserAssignee
from ..types import UNSET, Unset

T = TypeVar("T", bound="RequestWriteBase")


@attr.s(auto_attribs=True, repr=False)
class RequestWriteBase:
    """  """

    _assignees: Union[Unset, List[Union[RequestWriteUserAssignee, RequestWriteTeamAssignee]]] = UNSET
    _fields: Union[Unset, Fields] = UNSET
    _project_id: Union[Unset, str] = UNSET
    _requestor_id: Union[Unset, None, str] = UNSET
    _sample_groups: Union[Unset, List[RequestSampleGroupCreate]] = UNSET
    _scheduled_on: Union[Unset, datetime.date] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("assignees={}".format(repr(self._assignees)))
        fields.append("fields={}".format(repr(self._fields)))
        fields.append("project_id={}".format(repr(self._project_id)))
        fields.append("requestor_id={}".format(repr(self._requestor_id)))
        fields.append("sample_groups={}".format(repr(self._sample_groups)))
        fields.append("scheduled_on={}".format(repr(self._scheduled_on)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "RequestWriteBase({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        assignees: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._assignees, Unset):
            assignees = []
            for assignees_item_data in self._assignees:
                if isinstance(assignees_item_data, RequestWriteUserAssignee):
                    assignees_item = assignees_item_data.to_dict()

                else:
                    assignees_item = assignees_item_data.to_dict()

                assignees.append(assignees_item)

        fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._fields, Unset):
            fields = self._fields.to_dict()

        project_id = self._project_id
        requestor_id = self._requestor_id
        sample_groups: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._sample_groups, Unset):
            sample_groups = []
            for sample_groups_item_data in self._sample_groups:
                sample_groups_item = sample_groups_item_data.to_dict()

                sample_groups.append(sample_groups_item)

        scheduled_on: Union[Unset, str] = UNSET
        if not isinstance(self._scheduled_on, Unset):
            scheduled_on = self._scheduled_on.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if assignees is not UNSET:
            field_dict["assignees"] = assignees
        if fields is not UNSET:
            field_dict["fields"] = fields
        if project_id is not UNSET:
            field_dict["projectId"] = project_id
        if requestor_id is not UNSET:
            field_dict["requestorId"] = requestor_id
        if sample_groups is not UNSET:
            field_dict["sampleGroups"] = sample_groups
        if scheduled_on is not UNSET:
            field_dict["scheduledOn"] = scheduled_on

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        assignees = []
        _assignees = d.pop("assignees", UNSET)
        for assignees_item_data in _assignees or []:

            def _parse_assignees_item(
                data: Union[Dict[str, Any]]
            ) -> Union[RequestWriteUserAssignee, RequestWriteTeamAssignee]:
                assignees_item: Union[RequestWriteUserAssignee, RequestWriteTeamAssignee]
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    assignees_item = RequestWriteUserAssignee.from_dict(data)

                    return assignees_item
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                assignees_item = RequestWriteTeamAssignee.from_dict(data)

                return assignees_item

            assignees_item = _parse_assignees_item(assignees_item_data)

            assignees.append(assignees_item)

        fields: Union[Unset, Fields] = UNSET
        _fields = d.pop("fields", UNSET)
        if not isinstance(_fields, Unset):
            fields = Fields.from_dict(_fields)

        project_id = d.pop("projectId", UNSET)

        requestor_id = d.pop("requestorId", UNSET)

        sample_groups = []
        _sample_groups = d.pop("sampleGroups", UNSET)
        for sample_groups_item_data in _sample_groups or []:
            sample_groups_item = RequestSampleGroupCreate.from_dict(sample_groups_item_data)

            sample_groups.append(sample_groups_item)

        scheduled_on = None
        _scheduled_on = d.pop("scheduledOn", UNSET)
        if _scheduled_on is not None:
            scheduled_on = isoparse(cast(str, _scheduled_on)).date()

        request_write_base = cls(
            assignees=assignees,
            fields=fields,
            project_id=project_id,
            requestor_id=requestor_id,
            sample_groups=sample_groups,
            scheduled_on=scheduled_on,
        )

        request_write_base.additional_properties = d
        return request_write_base

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
    def assignees(self) -> List[Union[RequestWriteUserAssignee, RequestWriteTeamAssignee]]:
        if isinstance(self._assignees, Unset):
            raise NotPresentError(self, "assignees")
        return self._assignees

    @assignees.setter
    def assignees(self, value: List[Union[RequestWriteUserAssignee, RequestWriteTeamAssignee]]) -> None:
        self._assignees = value

    @assignees.deleter
    def assignees(self) -> None:
        self._assignees = UNSET

    @property
    def fields(self) -> Fields:
        if isinstance(self._fields, Unset):
            raise NotPresentError(self, "fields")
        return self._fields

    @fields.setter
    def fields(self, value: Fields) -> None:
        self._fields = value

    @fields.deleter
    def fields(self) -> None:
        self._fields = UNSET

    @property
    def project_id(self) -> str:
        if isinstance(self._project_id, Unset):
            raise NotPresentError(self, "project_id")
        return self._project_id

    @project_id.setter
    def project_id(self, value: str) -> None:
        self._project_id = value

    @project_id.deleter
    def project_id(self) -> None:
        self._project_id = UNSET

    @property
    def requestor_id(self) -> Optional[str]:
        if isinstance(self._requestor_id, Unset):
            raise NotPresentError(self, "requestor_id")
        return self._requestor_id

    @requestor_id.setter
    def requestor_id(self, value: Optional[str]) -> None:
        self._requestor_id = value

    @requestor_id.deleter
    def requestor_id(self) -> None:
        self._requestor_id = UNSET

    @property
    def sample_groups(self) -> List[RequestSampleGroupCreate]:
        if isinstance(self._sample_groups, Unset):
            raise NotPresentError(self, "sample_groups")
        return self._sample_groups

    @sample_groups.setter
    def sample_groups(self, value: List[RequestSampleGroupCreate]) -> None:
        self._sample_groups = value

    @sample_groups.deleter
    def sample_groups(self) -> None:
        self._sample_groups = UNSET

    @property
    def scheduled_on(self) -> datetime.date:
        if isinstance(self._scheduled_on, Unset):
            raise NotPresentError(self, "scheduled_on")
        return self._scheduled_on

    @scheduled_on.setter
    def scheduled_on(self, value: datetime.date) -> None:
        self._scheduled_on = value

    @scheduled_on.deleter
    def scheduled_on(self) -> None:
        self._scheduled_on = UNSET
