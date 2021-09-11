from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.request_task import RequestTask

T = TypeVar("T", bound="RequestTasksBulkCreateResponse")


@attr.s(auto_attribs=True, repr=False)
class RequestTasksBulkCreateResponse:
    """  """

    _tasks: List[RequestTask]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("tasks={}".format(repr(self._tasks)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "RequestTasksBulkCreateResponse({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        tasks = []
        for tasks_item_data in self._tasks:
            tasks_item = tasks_item_data.to_dict()

            tasks.append(tasks_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "tasks": tasks,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        tasks = []
        _tasks = d.pop("tasks")
        for tasks_item_data in _tasks:
            tasks_item = RequestTask.from_dict(tasks_item_data)

            tasks.append(tasks_item)

        request_tasks_bulk_create_response = cls(
            tasks=tasks,
        )

        request_tasks_bulk_create_response.additional_properties = d
        return request_tasks_bulk_create_response

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
    def tasks(self) -> List[RequestTask]:
        return self._tasks

    @tasks.setter
    def tasks(self, value: List[RequestTask]) -> None:
        self._tasks = value
