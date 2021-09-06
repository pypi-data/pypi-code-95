from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.relay_layer import RelayLayer
from ..types import UNSET, Unset

T = TypeVar("T", bound="RelayConfig")


@attr.s(auto_attribs=True)
class RelayConfig:
    """ """

    name: Union[Unset, str] = UNSET
    layers: Union[Unset, List[RelayLayer]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        layers: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.layers, Unset):
            layers = []
            for layers_item_data in self.layers:
                layers_item = layers_item_data.to_dict()

                layers.append(layers_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if layers is not UNSET:
            field_dict["layers"] = layers

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name", UNSET)

        layers = []
        _layers = d.pop("layers", UNSET)
        for layers_item_data in _layers or []:
            layers_item = RelayLayer.from_dict(layers_item_data)

            layers.append(layers_item)

        relay_config = cls(
            name=name,
            layers=layers,
        )

        relay_config.additional_properties = d
        return relay_config

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
