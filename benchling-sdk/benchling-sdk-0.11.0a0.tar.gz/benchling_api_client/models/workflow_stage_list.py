from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.workflow_stage import WorkflowStage

T = TypeVar("T", bound="WorkflowStageList")


@attr.s(auto_attribs=True, repr=False)
class WorkflowStageList:
    """  """

    _workflow_stages: List[WorkflowStage]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("workflow_stages={}".format(repr(self._workflow_stages)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowStageList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        workflow_stages = []
        for workflow_stages_item_data in self._workflow_stages:
            workflow_stages_item = workflow_stages_item_data.to_dict()

            workflow_stages.append(workflow_stages_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "workflowStages": workflow_stages,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        workflow_stages = []
        _workflow_stages = d.pop("workflowStages")
        for workflow_stages_item_data in _workflow_stages:
            workflow_stages_item = WorkflowStage.from_dict(workflow_stages_item_data)

            workflow_stages.append(workflow_stages_item)

        workflow_stage_list = cls(
            workflow_stages=workflow_stages,
        )

        workflow_stage_list.additional_properties = d
        return workflow_stage_list

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
    def workflow_stages(self) -> List[WorkflowStage]:
        return self._workflow_stages

    @workflow_stages.setter
    def workflow_stages(self, value: List[WorkflowStage]) -> None:
        self._workflow_stages = value
