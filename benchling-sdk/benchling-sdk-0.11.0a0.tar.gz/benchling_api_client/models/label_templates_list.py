from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.label_template import LabelTemplate

T = TypeVar("T", bound="LabelTemplatesList")


@attr.s(auto_attribs=True, repr=False)
class LabelTemplatesList:
    """  """

    _label_templates: List[LabelTemplate]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("label_templates={}".format(repr(self._label_templates)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "LabelTemplatesList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        label_templates = []
        for label_templates_item_data in self._label_templates:
            label_templates_item = label_templates_item_data.to_dict()

            label_templates.append(label_templates_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "labelTemplates": label_templates,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        label_templates = []
        _label_templates = d.pop("labelTemplates")
        for label_templates_item_data in _label_templates:
            label_templates_item = LabelTemplate.from_dict(label_templates_item_data)

            label_templates.append(label_templates_item)

        label_templates_list = cls(
            label_templates=label_templates,
        )

        label_templates_list.additional_properties = d
        return label_templates_list

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
    def label_templates(self) -> List[LabelTemplate]:
        return self._label_templates

    @label_templates.setter
    def label_templates(self, value: List[LabelTemplate]) -> None:
        self._label_templates = value
