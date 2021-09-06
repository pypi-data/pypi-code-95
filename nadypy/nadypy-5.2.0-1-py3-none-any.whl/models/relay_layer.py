from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.relay_layer_argument import RelayLayerArgument
from ..types import UNSET, Unset

T = TypeVar("T", bound="RelayLayer")


@attr.s(auto_attribs=True)
class RelayLayer:
    """ """

    layer: Union[Unset, str] = UNSET
    arguments: Union[Unset, List[RelayLayerArgument]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        layer = self.layer
        arguments: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.arguments, Unset):
            arguments = []
            for arguments_item_data in self.arguments:
                arguments_item = arguments_item_data.to_dict()

                arguments.append(arguments_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if layer is not UNSET:
            field_dict["layer"] = layer
        if arguments is not UNSET:
            field_dict["arguments"] = arguments

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        layer = d.pop("layer", UNSET)

        arguments = []
        _arguments = d.pop("arguments", UNSET)
        for arguments_item_data in _arguments or []:
            arguments_item = RelayLayerArgument.from_dict(arguments_item_data)

            arguments.append(arguments_item)

        relay_layer = cls(
            layer=layer,
            arguments=arguments,
        )

        relay_layer.additional_properties = d
        return relay_layer

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
