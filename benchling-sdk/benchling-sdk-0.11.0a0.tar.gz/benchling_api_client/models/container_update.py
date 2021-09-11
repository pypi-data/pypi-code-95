from typing import Any, Dict, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.container_quantity import ContainerQuantity
from ..models.container_volume import ContainerVolume
from ..models.fields import Fields
from ..types import UNSET, Unset

T = TypeVar("T", bound="ContainerUpdate")


@attr.s(auto_attribs=True, repr=False)
class ContainerUpdate:
    """  """

    _project_id: Union[Unset, None, str] = UNSET
    _quantity: Union[Unset, ContainerQuantity] = UNSET
    _volume: Union[Unset, ContainerVolume] = UNSET
    _fields: Union[Unset, Fields] = UNSET
    _name: Union[Unset, str] = UNSET
    _parent_storage_id: Union[Unset, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("project_id={}".format(repr(self._project_id)))
        fields.append("quantity={}".format(repr(self._quantity)))
        fields.append("volume={}".format(repr(self._volume)))
        fields.append("fields={}".format(repr(self._fields)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("parent_storage_id={}".format(repr(self._parent_storage_id)))
        return "ContainerUpdate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        project_id = self._project_id
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
        field_dict.update({})
        if project_id is not UNSET:
            field_dict["projectId"] = project_id
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
        project_id = d.pop("projectId", UNSET)

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

        container_update = cls(
            project_id=project_id,
            quantity=quantity,
            volume=volume,
            fields=fields,
            name=name,
            parent_storage_id=parent_storage_id,
        )

        return container_update

    @property
    def project_id(self) -> Optional[str]:
        if isinstance(self._project_id, Unset):
            raise NotPresentError(self, "project_id")
        return self._project_id

    @project_id.setter
    def project_id(self, value: Optional[str]) -> None:
        self._project_id = value

    @project_id.deleter
    def project_id(self) -> None:
        self._project_id = UNSET

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
