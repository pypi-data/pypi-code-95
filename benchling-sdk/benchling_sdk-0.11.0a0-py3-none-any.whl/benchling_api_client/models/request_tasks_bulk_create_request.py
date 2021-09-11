from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.request_tasks_bulk_create import RequestTasksBulkCreate

T = TypeVar("T", bound="RequestTasksBulkCreateRequest")


@attr.s(auto_attribs=True, repr=False)
class RequestTasksBulkCreateRequest:
    """  """

    _tasks: List[RequestTasksBulkCreate]

    def __repr__(self):
        fields = []
        fields.append("tasks={}".format(repr(self._tasks)))
        return "RequestTasksBulkCreateRequest({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        tasks = []
        for tasks_item_data in self._tasks:
            tasks_item = tasks_item_data.to_dict()

            tasks.append(tasks_item)

        field_dict: Dict[str, Any] = {}
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
            tasks_item = RequestTasksBulkCreate.from_dict(tasks_item_data)

            tasks.append(tasks_item)

        request_tasks_bulk_create_request = cls(
            tasks=tasks,
        )

        return request_tasks_bulk_create_request

    @property
    def tasks(self) -> List[RequestTasksBulkCreate]:
        return self._tasks

    @tasks.setter
    def tasks(self, value: List[RequestTasksBulkCreate]) -> None:
        self._tasks = value
