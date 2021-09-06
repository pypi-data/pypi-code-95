from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.function_parameter import FunctionParameter
from ..types import UNSET, Unset

T = TypeVar("T", bound="ClassSpec")


@attr.s(auto_attribs=True)
class ClassSpec:
    """ """

    name: Union[Unset, str] = UNSET
    class_: Union[Unset, str] = UNSET
    params: Union[Unset, List[FunctionParameter]] = UNSET
    description: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        class_ = self.class_
        params: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.params, Unset):
            params = []
            for params_item_data in self.params:
                params_item = params_item_data.to_dict()

                params.append(params_item)

        description = self.description

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if class_ is not UNSET:
            field_dict["class"] = class_
        if params is not UNSET:
            field_dict["params"] = params
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name", UNSET)

        class_ = d.pop("class", UNSET)

        params = []
        _params = d.pop("params", UNSET)
        for params_item_data in _params or []:
            params_item = FunctionParameter.from_dict(params_item_data)

            params.append(params_item)

        description = d.pop("description", UNSET)

        class_spec = cls(
            name=name,
            class_=class_,
            params=params,
            description=description,
        )

        class_spec.additional_properties = d
        return class_spec

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
