from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..models.setting_option import SettingOption
from ..types import UNSET, Unset

T = TypeVar("T", bound="ModuleSetting")


@attr.s(auto_attribs=True)
class ModuleSetting:
    """ """

    type: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    value: Union[None, Unset, bool, int, str] = UNSET
    options: Union[Unset, List[SettingOption]] = UNSET
    editable: Union[Unset, bool] = UNSET
    description: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        type = self.type
        name = self.name
        value: Union[None, Unset, bool, int, str]
        if isinstance(self.value, Unset):
            value = UNSET
        elif self.value is None:
            value = None
        else:
            value = self.value

        options: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.options, Unset):
            options = []
            for options_item_data in self.options:
                options_item = options_item_data.to_dict()

                options.append(options_item)

        editable = self.editable
        description = self.description

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if type is not UNSET:
            field_dict["type"] = type
        if name is not UNSET:
            field_dict["name"] = name
        if value is not UNSET:
            field_dict["value"] = value
        if options is not UNSET:
            field_dict["options"] = options
        if editable is not UNSET:
            field_dict["editable"] = editable
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        type = d.pop("type", UNSET)

        name = d.pop("name", UNSET)

        def _parse_value(data: object) -> Union[None, Unset, bool, int, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool, int, str], data)

        value = _parse_value(d.pop("value", UNSET))

        options = []
        _options = d.pop("options", UNSET)
        for options_item_data in _options or []:
            options_item = SettingOption.from_dict(options_item_data)

            options.append(options_item)

        editable = d.pop("editable", UNSET)

        description = d.pop("description", UNSET)

        module_setting = cls(
            type=type,
            name=name,
            value=value,
            options=options,
            editable=editable,
            description=description,
        )

        module_setting.additional_properties = d
        return module_setting

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
