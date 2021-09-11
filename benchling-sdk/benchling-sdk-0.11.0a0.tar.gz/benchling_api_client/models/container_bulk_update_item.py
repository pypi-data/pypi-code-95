from typing import Any, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.container_quantity import ContainerQuantity
from ..models.container_volume import ContainerVolume
from ..models.fields import Fields
from ..types import UNSET, Unset

T = TypeVar("T", bound="ContainerBulkUpdateItem")


@attr.s(auto_attribs=True, repr=False)
class ContainerBulkUpdateItem:
    """  """

    _container_id: str
    _quantity: Union[Unset, ContainerQuantity] = UNSET
    _volume: Union[Unset, ContainerVolume] = UNSET
    _fields: Union[Unset, Fields] = UNSET
    _name: Union[Unset, str] = UNSET
    _parent_storage_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("container_id={}".format(repr(self._container_id)))
        fields.append("quantity={}".format(repr(self._quantity)))
        fields.append("volume={}".format(repr(self._volume)))
        fields.append("fields={}".format(repr(self._fields)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("parent_storage_id={}".format(repr(self._parent_storage_id)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "ContainerBulkUpdateItem({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        container_id = self._container_id
        quantity: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._quantity, Unset):
            quantity = self._quantity.to_dict()

        volume: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._volume, Unset):
            volume = self._volume.to_dict()

        fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._fields, Unset):
            fields = self._fields.to_dict()

        name = self._name
        parent_storage_id = self._parent_storage_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "containerId": container_id,
            }
        )
        if quantity is not UNSET:
            field_dict["quantity"] = quantity
        if volume is not UNSET:
            field_dict["volume"] = volume
        if fields is not UNSET:
            field_dict["fields"] = fields
        if name is not UNSET:
            field_dict["name"] = name
        if parent_storage_id is not UNSET:
            field_dict["parentStorageId"] = parent_storage_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        container_id = d.pop("containerId")

        quantity: Union[Unset, ContainerQuantity] = UNSET
        _quantity = d.pop("quantity", UNSET)
        if not isinstance(_quantity, Unset):
            quantity = ContainerQuantity.from_dict(_quantity)

        volume: Union[Unset, ContainerVolume] = UNSET
        _volume = d.pop("volume", UNSET)
        if not isinstance(_volume, Unset):
            volume = ContainerVolume.from_dict(_volume)

        fields: Union[Unset, Fields] = UNSET
        _fields = d.pop("fields", UNSET)
        if not isinstance(_fields, Unset):
            fields = Fields.from_dict(_fields)

        name = d.pop("name", UNSET)

        parent_storage_id = d.pop("parentStorageId", UNSET)

        container_bulk_update_item = cls(
            container_id=container_id,
            quantity=quantity,
            volume=volume,
            fields=fields,
            name=name,
            parent_storage_id=parent_storage_id,
        )

        container_bulk_update_item.additional_properties = d
        return container_bulk_update_item

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
    def container_id(self) -> str:
        return self._container_id

    @container_id.setter
    def container_id(self, value: str) -> None:
        self._container_id = value

    @property
    def quantity(self) -> ContainerQuantity:
        if isinstance(self._quantity, Unset):
            raise NotPresentError(self, "quantity")
        return self._quantity

    @quantity.setter
    def quantity(self, value: ContainerQuantity) -> None:
        self._quantity = value

    @quantity.deleter
    def quantity(self) -> None:
        self._quantity = UNSET

    @property
    def volume(self) -> ContainerVolume:
        if isinstance(self._volume, Unset):
            raise NotPresentError(self, "volume")
        return self._volume

    @volume.setter
    def volume(self, value: ContainerVolume) -> None:
        self._volume = value

    @volume.deleter
    def volume(self) -> None:
        self._volume = UNSET

    @property
    def fields(self) -> Fields:
        if isinstance(self._fields, Unset):
            raise NotPresentError(self, "fields")
        return self._fields

    @fields.setter
    def fields(self, value: Fields) -> None:
        self._fields = value

    @fields.deleter
    def fields(self) -> None:
        self._fields = UNSET

    @property
    def name(self) -> str:
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @name.deleter
    def name(self) -> None:
        self._name = UNSET

    @property
    def parent_storage_id(self) -> str:
        if isinstance(self._parent_storage_id, Unset):
            raise NotPresentError(self, "parent_storage_id")
        return self._parent_storage_id

    @parent_storage_id.setter
    def parent_storage_id(self, value: str) -> None:
        self._parent_storage_id = value

    @parent_storage_id.deleter
    def parent_storage_id(self) -> None:
        self._parent_storage_id = UNSET
