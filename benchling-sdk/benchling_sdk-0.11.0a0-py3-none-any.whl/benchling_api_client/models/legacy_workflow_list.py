from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.legacy_workflow import LegacyWorkflow

T = TypeVar("T", bound="LegacyWorkflowList")


@attr.s(auto_attribs=True, repr=False)
class LegacyWorkflowList:
    """  """

    _workflows: List[LegacyWorkflow]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("workflows={}".format(repr(self._workflows)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "LegacyWorkflowList({})".format(", ".join(fields))

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
            workflows_item = LegacyWorkflow.from_dict(workflows_item_data)

            workflows.append(workflows_item)

        legacy_workflow_list = cls(
            workflows=workflows,
        )

        legacy_workflow_list.additional_properties = d
        return legacy_workflow_list

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
    def workflows(self) -> List[LegacyWorkflow]:
        return self._workflows

    @workflows.setter
    def workflows(self, value: List[LegacyWorkflow]) -> None:
        self._workflows = value
