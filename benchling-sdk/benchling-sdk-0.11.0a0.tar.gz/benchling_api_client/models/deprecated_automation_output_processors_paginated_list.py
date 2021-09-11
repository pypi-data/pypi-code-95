from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.automation_output_processor import AutomationOutputProcessor

T = TypeVar("T", bound="DeprecatedAutomationOutputProcessorsPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class DeprecatedAutomationOutputProcessorsPaginatedList:
    """ Deprecated - A paginated list of automation output processors """

    _automation_output_processors: List[AutomationOutputProcessor]
    _next_token: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("automation_output_processors={}".format(repr(self._automation_output_processors)))
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "DeprecatedAutomationOutputProcessorsPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        automation_output_processors = []
        for automation_output_processors_item_data in self._automation_output_processors:
            automation_output_processors_item = automation_output_processors_item_data.to_dict()

            automation_output_processors.append(automation_output_processors_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "automationOutputProcessors": automation_output_processors,
                "nextToken": next_token,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        automation_output_processors = []
        _automation_output_processors = d.pop("automationOutputProcessors")
        for automation_output_processors_item_data in _automation_output_processors:
            automation_output_processors_item = AutomationOutputProcessor.from_dict(
                automation_output_processors_item_data
            )

            automation_output_processors.append(automation_output_processors_item)

        next_token = d.pop("nextToken")

        deprecated_automation_output_processors_paginated_list = cls(
            automation_output_processors=automation_output_processors,
            next_token=next_token,
        )

        deprecated_automation_output_processors_paginated_list.additional_properties = d
        return deprecated_automation_output_processors_paginated_list

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
    def automation_output_processors(self) -> List[AutomationOutputProcessor]:
        return self._automation_output_processors

    @automation_output_processors.setter
    def automation_output_processors(self, value: List[AutomationOutputProcessor]) -> None:
        self._automation_output_processors = value

    @property
    def next_token(self) -> str:
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value
