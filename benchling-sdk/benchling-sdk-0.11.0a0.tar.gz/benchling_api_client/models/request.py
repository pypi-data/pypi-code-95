import datetime
from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..extensions import NotPresentError
from ..models.fields import Fields
from ..models.request_creator import RequestCreator
from ..models.request_requestor import RequestRequestor
from ..models.request_sample_group import RequestSampleGroup
from ..models.request_schema_property import RequestSchemaProperty
from ..models.request_status import RequestStatus
from ..models.request_task import RequestTask
from ..models.request_team_assignee import RequestTeamAssignee
from ..models.request_user_assignee import RequestUserAssignee
from ..types import UNSET, Unset

T = TypeVar("T", bound="Request")


@attr.s(auto_attribs=True, repr=False)
class Request:
    """  """

    _assignees: List[Union[RequestUserAssignee, RequestTeamAssignee]]
    _created_at: str
    _creator: RequestCreator
    _display_id: str
    _fields: Fields
    _id: str
    _request_status: RequestStatus
    _requestor: RequestRequestor
    _sample_groups: List[RequestSampleGroup]
    _schema: RequestSchemaProperty
    _web_url: str
    _scheduled_on: Optional[datetime.date]
    _api_url: Union[Unset, str] = UNSET
    _project_id: Union[Unset, str] = UNSET
    _tasks: Union[Unset, List[RequestTask]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("assignees={}".format(repr(self._assignees)))
        fields.append("created_at={}".format(repr(self._created_at)))
        fields.append("creator={}".format(repr(self._creator)))
        fields.append("display_id={}".format(repr(self._display_id)))
        fields.append("fields={}".format(repr(self._fields)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("request_status={}".format(repr(self._request_status)))
        fields.append("requestor={}".format(repr(self._requestor)))
        fields.append("sample_groups={}".format(repr(self._sample_groups)))
        fields.append("schema={}".format(repr(self._schema)))
        fields.append("web_url={}".format(repr(self._web_url)))
        fields.append("api_url={}".format(repr(self._api_url)))
        fields.append("project_id={}".format(repr(self._project_id)))
        fields.append("scheduled_on={}".format(repr(self._scheduled_on)))
        fields.append("tasks={}".format(repr(self._tasks)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "Request({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        assignees = []
        for assignees_item_data in self._assignees:
            if isinstance(assignees_item_data, RequestUserAssignee):
                assignees_item = assignees_item_data.to_dict()

            else:
                assignees_item = assignees_item_data.to_dict()

            assignees.append(assignees_item)

        created_at = self._created_at
        creator = self._creator.to_dict()

        display_id = self._display_id
        fields = self._fields.to_dict()

        id = self._id
        request_status = self._request_status.value

        requestor = self._requestor.to_dict()

        sample_groups = []
        for sample_groups_item_data in self._sample_groups:
            sample_groups_item = sample_groups_item_data.to_dict()

            sample_groups.append(sample_groups_item)

        schema = self._schema.to_dict()

        web_url = self._web_url
        api_url = self._api_url
        project_id = self._project_id
        scheduled_on = self._scheduled_on.isoformat() if self._scheduled_on else None
        tasks: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._tasks, Unset):
            tasks = []
            for tasks_item_data in self._tasks:
                tasks_item = tasks_item_data.to_dict()

                tasks.append(tasks_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "assignees": assignees,
                "createdAt": created_at,
                "creator": creator,
                "displayId": display_id,
                "fields": fields,
                "id": id,
                "requestStatus": request_status,
                "requestor": requestor,
                "sampleGroups": sample_groups,
                "schema": schema,
                "webURL": web_url,
                "scheduledOn": scheduled_on,
            }
        )
        if api_url is not UNSET:
            field_dict["apiURL"] = api_url
        if project_id is not UNSET:
            field_dict["projectId"] = project_id
        if tasks is not UNSET:
            field_dict["tasks"] = tasks

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        assignees = []
        _assignees = d.pop("assignees")
        for assignees_item_data in _assignees:

            def _parse_assignees_item(
                data: Union[Dict[str, Any]]
            ) -> Union[RequestUserAssignee, RequestTeamAssignee]:
                assignees_item: Union[RequestUserAssignee, RequestTeamAssignee]
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    assignees_item = RequestUserAssignee.from_dict(data)

                    return assignees_item
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                assignees_item = RequestTeamAssignee.from_dict(data)

                return assignees_item

            assignees_item = _parse_assignees_item(assignees_item_data)

            assignees.append(assignees_item)

        created_at = d.pop("createdAt")

        creator = RequestCreator.from_dict(d.pop("creator"))

        display_id = d.pop("displayId")

        fields = Fields.from_dict(d.pop("fields"))

        id = d.pop("id")

        request_status = RequestStatus(d.pop("requestStatus"))

        requestor = RequestRequestor.from_dict(d.pop("requestor"))

        sample_groups = []
        _sample_groups = d.pop("sampleGroups")
        for sample_groups_item_data in _sample_groups:
            sample_groups_item = RequestSampleGroup.from_dict(sample_groups_item_data)

            sample_groups.append(sample_groups_item)

        schema = RequestSchemaProperty.from_dict(d.pop("schema"))

        web_url = d.pop("webURL")

        api_url = d.pop("apiURL", UNSET)

        project_id = d.pop("projectId", UNSET)

        scheduled_on = None
        _scheduled_on = d.pop("scheduledOn")
        if _scheduled_on is not None:
            scheduled_on = isoparse(cast(str, _scheduled_on)).date()

        tasks = []
        _tasks = d.pop("tasks", UNSET)
        for tasks_item_data in _tasks or []:
            tasks_item = RequestTask.from_dict(tasks_item_data)

            tasks.append(tasks_item)

        request = cls(
            assignees=assignees,
            created_at=created_at,
            creator=creator,
            display_id=display_id,
            fields=fields,
            id=id,
            request_status=request_status,
            requestor=requestor,
            sample_groups=sample_groups,
            schema=schema,
            web_url=web_url,
            api_url=api_url,
            project_id=project_id,
            scheduled_on=scheduled_on,
            tasks=tasks,
        )

        request.additional_properties = d
        return request

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
    def assignees(self) -> List[Union[RequestUserAssignee, RequestTeamAssignee]]:
        return self._assignees

    @assignees.setter
    def assignees(self, value: List[Union[RequestUserAssignee, RequestTeamAssignee]]) -> None:
        self._assignees = value

    @property
    def created_at(self) -> str:
        return self._created_at

    @created_at.setter
    def created_at(self, value: str) -> None:
        self._created_at = value

    @property
    def creator(self) -> RequestCreator:
        return self._creator

    @creator.setter
    def creator(self, value: RequestCreator) -> None:
        self._creator = value

    @property
    def display_id(self) -> str:
        return self._display_id

    @display_id.setter
    def display_id(self, value: str) -> None:
        self._display_id = value

    @property
    def fields(self) -> Fields:
        return self._fields

    @fields.setter
    def fields(self, value: Fields) -> None:
        self._fields = value

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @property
    def request_status(self) -> RequestStatus:
        return self._request_status

    @request_status.setter
    def request_status(self, value: RequestStatus) -> None:
        self._request_status = value

    @property
    def requestor(self) -> RequestRequestor:
        return self._requestor

    @requestor.setter
    def requestor(self, value: RequestRequestor) -> None:
        self._requestor = value

    @property
    def sample_groups(self) -> List[RequestSampleGroup]:
        return self._sample_groups

    @sample_groups.setter
    def sample_groups(self, value: List[RequestSampleGroup]) -> None:
        self._sample_groups = value

    @property
    def schema(self) -> RequestSchemaProperty:
        return self._schema

    @schema.setter
    def schema(self, value: RequestSchemaProperty) -> None:
        self._schema = value

    @property
    def web_url(self) -> str:
        return self._web_url

    @web_url.setter
    def web_url(self, value: str) -> None:
        self._web_url = value

    @property
    def api_url(self) -> str:
        if isinstance(self._api_url, Unset):
            raise NotPresentError(self, "api_url")
        return self._api_url

    @api_url.setter
    def api_url(self, value: str) -> None:
        self._api_url = value

    @api_url.deleter
    def api_url(self) -> None:
        self._api_url = UNSET

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
    def scheduled_on(self) -> Optional[datetime.date]:
        return self._scheduled_on

    @scheduled_on.setter
    def scheduled_on(self, value: Optional[datetime.date]) -> None:
        self._scheduled_on = value

    @property
    def tasks(self) -> List[RequestTask]:
        if isinstance(self._tasks, Unset):
            raise NotPresentError(self, "tasks")
        return self._tasks

    @tasks.setter
    def tasks(self, value: List[RequestTask]) -> None:
        self._tasks = value

    @tasks.deleter
    def tasks(self) -> None:
        self._tasks = UNSET
