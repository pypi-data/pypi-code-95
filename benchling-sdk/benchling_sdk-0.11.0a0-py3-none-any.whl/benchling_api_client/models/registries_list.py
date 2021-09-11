from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.registry import Registry

T = TypeVar("T", bound="RegistriesList")


@attr.s(auto_attribs=True, repr=False)
class RegistriesList:
    """  """

    _registries: List[Registry]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("registries={}".format(repr(self._registries)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "RegistriesList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        registries = []
        for registries_item_data in self._registries:
            registries_item = registries_item_data.to_dict()

            registries.append(registries_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "registries": registries,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        registries = []
        _registries = d.pop("registries")
        for registries_item_data in _registries:
            registries_item = Registry.from_dict(registries_item_data)

            registries.append(registries_item)

        registries_list = cls(
            registries=registries,
        )

        registries_list.additional_properties = d
        return registries_list

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
    def registries(self) -> List[Registry]:
        return self._registries

    @registries.setter
    def registries(self, value: List[Registry]) -> None:
        self._registries = value
