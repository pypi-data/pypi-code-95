from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.workflow import Workflow

T = TypeVar("T", bound="WorkflowList")


@attr.s(auto_attribs=True, repr=False)
class WorkflowList:
    """  """

    _workflows: List[Workflow]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("workflows={}".format(repr(self._workflows)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        workflows = []
        for workflows_item_data in self._workflows:
            workflows_item = workflows_item_data.to_dict()

            workflows.append(workflows_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "workflows": workflows,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        workflows = []
        _workflows = d.pop("workflows")
        for workflows_item_data in _workflows:
            workflows_item = Workflow.from_dict(workflows_item_data)

            workflows.append(workflows_item)

        workflow_list = cls(
            workflows=workflows,
        )

        workflow_list.additional_properties = d
        return workflow_list

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
    def workflows(self) -> List[Workflow]:
        return self._workflows

    @workflows.setter
    def workflows(self, value: List[Workflow]) -> None:
        self._workflows = value
