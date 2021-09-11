from typing import Any, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.container_quantity import ContainerQuantity
from ..models.container_volume import ContainerVolume
from ..models.multiple_containers_transfer_source_concentration import (
    MultipleContainersTransferSourceConcentration,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="MultipleContainersTransfer")


@attr.s(auto_attribs=True, repr=False)
class MultipleContainersTransfer:
    """  """

    _destination_container_id: str
    _transfer_volume: ContainerVolume
    _final_quantity: Union[Unset, ContainerQuantity] = UNSET
    _final_volume: Union[Unset, ContainerVolume] = UNSET
    _source_concentration: Union[Unset, MultipleContainersTransferSourceConcentration] = UNSET
    _source_batch_id: Union[Unset, str] = UNSET
    _source_container_id: Union[Unset, str] = UNSET
    _source_entity_id: Union[Unset, str] = UNSET
    _transfer_quantity: Union[Unset, ContainerQuantity] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("destination_container_id={}".format(repr(self._destination_container_id)))
        fields.append("transfer_volume={}".format(repr(self._transfer_volume)))
        fields.append("final_quantity={}".format(repr(self._final_quantity)))
        fields.append("final_volume={}".format(repr(self._final_volume)))
        fields.append("source_concentration={}".format(repr(self._source_concentration)))
        fields.append("source_batch_id={}".format(repr(self._source_batch_id)))
        fields.append("source_container_id={}".format(repr(self._source_container_id)))
        fields.append("source_entity_id={}".format(repr(self._source_entity_id)))
        fields.append("transfer_quantity={}".format(repr(self._transfer_quantity)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "MultipleContainersTransfer({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        destination_container_id = self._destination_container_id
        transfer_volume = self._transfer_volume.to_dict()

        final_quantity: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._final_quantity, Unset):
            final_quantity = self._final_quantity.to_dict()

        final_volume: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._final_volume, Unset):
            final_volume = self._final_volume.to_dict()

        source_concentration: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._source_concentration, Unset):
            source_concentration = self._source_concentration.to_dict()

        source_batch_id = self._source_batch_id
        source_container_id = self._source_container_id
        source_entity_id = self._source_entity_id
        transfer_quantity: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._transfer_quantity, Unset):
            transfer_quantity = self._transfer_quantity.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "destinationContainerId": destination_container_id,
                "transferVolume": transfer_volume,
            }
        )
        if final_quantity is not UNSET:
            field_dict["finalQuantity"] = final_quantity
        if final_volume is not UNSET:
            field_dict["finalVolume"] = final_volume
        if source_concentration is not UNSET:
            field_dict["sourceConcentration"] = source_concentration
        if source_batch_id is not UNSET:
            field_dict["sourceBatchId"] = source_batch_id
        if source_container_id is not UNSET:
            field_dict["sourceContainerId"] = source_container_id
        if source_entity_id is not UNSET:
            field_dict["sourceEntityId"] = source_entity_id
        if transfer_quantity is not UNSET:
            field_dict["transferQuantity"] = transfer_quantity

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        destination_container_id = d.pop("destinationContainerId")

        transfer_volume = ContainerVolume.from_dict(d.pop("transferVolume"))

        final_quantity: Union[Unset, ContainerQuantity] = UNSET
        _final_quantity = d.pop("finalQuantity", UNSET)
        if not isinstance(_final_quantity, Unset):
            final_quantity = ContainerQuantity.from_dict(_final_quantity)

        final_volume: Union[Unset, ContainerVolume] = UNSET
        _final_volume = d.pop("finalVolume", UNSET)
        if not isinstance(_final_volume, Unset):
            final_volume = ContainerVolume.from_dict(_final_volume)

        source_concentration: Union[Unset, MultipleContainersTransferSourceConcentration] = UNSET
        _source_concentration = d.pop("sourceConcentration", UNSET)
        if not isinstance(_source_concentration, Unset):
            source_concentration = MultipleContainersTransferSourceConcentration.from_dict(
                _source_concentration
            )

        source_batch_id = d.pop("sourceBatchId", UNSET)

        source_container_id = d.pop("sourceContainerId", UNSET)

        source_entity_id = d.pop("sourceEntityId", UNSET)

        transfer_quantity: Union[Unset, ContainerQuantity] = UNSET
        _transfer_quantity = d.pop("transferQuantity", UNSET)
        if not isinstance(_transfer_quantity, Unset):
            transfer_quantity = ContainerQuantity.from_dict(_transfer_quantity)

        multiple_containers_transfer = cls(
            destination_container_id=destination_container_id,
            transfer_volume=transfer_volume,
            final_quantity=final_quantity,
            final_volume=final_volume,
            source_concentration=source_concentration,
            source_batch_id=source_batch_id,
            source_container_id=source_container_id,
            source_entity_id=source_entity_id,
            transfer_quantity=transfer_quantity,
        )

        multiple_containers_transfer.additional_properties = d
        return multiple_containers_transfer

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
    def destination_container_id(self) -> str:
        return self._destination_container_id

    @destination_container_id.setter
    def destination_container_id(self, value: str) -> None:
        self._destination_container_id = value

    @property
    def transfer_volume(self) -> ContainerVolume:
        return self._transfer_volume

    @transfer_volume.setter
    def transfer_volume(self, value: ContainerVolume) -> None:
        self._transfer_volume = value

    @property
    def final_quantity(self) -> ContainerQuantity:
        if isinstance(self._final_quantity, Unset):
            raise NotPresentError(self, "final_quantity")
        return self._final_quantity

    @final_quantity.setter
    def final_quantity(self, value: ContainerQuantity) -> None:
        self._final_quantity = value

    @final_quantity.deleter
    def final_quantity(self) -> None:
        self._final_quantity = UNSET

    @property
    def final_volume(self) -> ContainerVolume:
        if isinstance(self._final_volume, Unset):
            raise NotPresentError(self, "final_volume")
        return self._final_volume

    @final_volume.setter
    def final_volume(self, value: ContainerVolume) -> None:
        self._final_volume = value

    @final_volume.deleter
    def final_volume(self) -> None:
        self._final_volume = UNSET

    @property
    def source_concentration(self) -> MultipleContainersTransferSourceConcentration:
        if isinstance(self._source_concentration, Unset):
            raise NotPresentError(self, "source_concentration")
        return self._source_concentration

    @source_concentration.setter
    def source_concentration(self, value: MultipleContainersTransferSourceConcentration) -> None:
        self._source_concentration = value

    @source_concentration.deleter
    def source_concentration(self) -> None:
        self._source_concentration = UNSET

    @property
    def source_batch_id(self) -> str:
        if isinstance(self._source_batch_id, Unset):
            raise NotPresentError(self, "source_batch_id")
        return self._source_batch_id

    @source_batch_id.setter
    def source_batch_id(self, value: str) -> None:
        self._source_batch_id = value

    @source_batch_id.deleter
    def source_batch_id(self) -> None:
        self._source_batch_id = UNSET

    @property
    def source_container_id(self) -> str:
        if isinstance(self._source_container_id, Unset):
            raise NotPresentError(self, "source_container_id")
        return self._source_container_id

    @source_container_id.setter
    def source_container_id(self, value: str) -> None:
        self._source_container_id = value

    @source_container_id.deleter
    def source_container_id(self) -> None:
        self._source_container_id = UNSET

    @property
    def source_entity_id(self) -> str:
        if isinstance(self._source_entity_id, Unset):
            raise NotPresentError(self, "source_entity_id")
        return self._source_entity_id

    @source_entity_id.setter
    def source_entity_id(self, value: str) -> None:
        self._source_entity_id = value

    @source_entity_id.deleter
    def source_entity_id(self) -> None:
        self._source_entity_id = UNSET

    @property
    def transfer_quantity(self) -> ContainerQuantity:
        if isinstance(self._transfer_quantity, Unset):
            raise NotPresentError(self, "transfer_quantity")
        return self._transfer_quantity

    @transfer_quantity.setter
    def transfer_quantity(self, value: ContainerQuantity) -> None:
        self._transfer_quantity = value

    @transfer_quantity.deleter
    def transfer_quantity(self) -> None:
        self._transfer_quantity = UNSET
