from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.container_quantity import ContainerQuantity
from ..models.container_transfer_destination_contents_item import ContainerTransferDestinationContentsItem
from ..models.container_volume import ContainerVolume
from ..types import UNSET, Unset

T = TypeVar("T", bound="ContainerTransfer")


@attr.s(auto_attribs=True, repr=False)
class ContainerTransfer:
    """  """

    _transfer_volume: ContainerVolume
    _destination_contents: Union[Unset, List[ContainerTransferDestinationContentsItem]] = UNSET
    _destination_quantity: Union[Unset, ContainerQuantity] = UNSET
    _destination_volume: Union[Unset, ContainerVolume] = UNSET
    _source_batch_id: Union[Unset, str] = UNSET
    _source_container_id: Union[Unset, str] = UNSET
    _source_entity_id: Union[Unset, str] = UNSET
    _transfer_quantity: Union[Unset, ContainerQuantity] = UNSET

    def __repr__(self):
        fields = []
        fields.append("transfer_volume={}".format(repr(self._transfer_volume)))
        fields.append("destination_contents={}".format(repr(self._destination_contents)))
        fields.append("destination_quantity={}".format(repr(self._destination_quantity)))
        fields.append("destination_volume={}".format(repr(self._destination_volume)))
        fields.append("source_batch_id={}".format(repr(self._source_batch_id)))
        fields.append("source_container_id={}".format(repr(self._source_container_id)))
        fields.append("source_entity_id={}".format(repr(self._source_entity_id)))
        fields.append("transfer_quantity={}".format(repr(self._transfer_quantity)))
        return "ContainerTransfer({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        transfer_volume = self._transfer_volume.to_dict()

        destination_contents: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._destination_contents, Unset):
            destination_contents = []
            for destination_contents_item_data in self._destination_contents:
                destination_contents_item = destination_contents_item_data.to_dict()

                destination_contents.append(destination_contents_item)

        destination_quantity: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._destination_quantity, Unset):
            destination_quantity = self._destination_quantity.to_dict()

        destination_volume: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._destination_volume, Unset):
            destination_volume = self._destination_volume.to_dict()

        source_batch_id = self._source_batch_id
        source_container_id = self._source_container_id
        source_entity_id = self._source_entity_id
        transfer_quantity: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._transfer_quantity, Unset):
            transfer_quantity = self._transfer_quantity.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "transferVolume": transfer_volume,
            }
        )
        if destination_contents is not UNSET:
            field_dict["destinationContents"] = destination_contents
        if destination_quantity is not UNSET:
            field_dict["destinationQuantity"] = destination_quantity
        if destination_volume is not UNSET:
            field_dict["destinationVolume"] = destination_volume
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
        transfer_volume = ContainerVolume.from_dict(d.pop("transferVolume"))

        destination_contents = []
        _destination_contents = d.pop("destinationContents", UNSET)
        for destination_contents_item_data in _destination_contents or []:
            destination_contents_item = ContainerTransferDestinationContentsItem.from_dict(
                destination_contents_item_data
            )

            destination_contents.append(destination_contents_item)

        destination_quantity: Union[Unset, ContainerQuantity] = UNSET
        _destination_quantity = d.pop("destinationQuantity", UNSET)
        if not isinstance(_destination_quantity, Unset):
            destination_quantity = ContainerQuantity.from_dict(_destination_quantity)

        destination_volume: Union[Unset, ContainerVolume] = UNSET
        _destination_volume = d.pop("destinationVolume", UNSET)
        if not isinstance(_destination_volume, Unset):
            destination_volume = ContainerVolume.from_dict(_destination_volume)

        source_batch_id = d.pop("sourceBatchId", UNSET)

        source_container_id = d.pop("sourceContainerId", UNSET)

        source_entity_id = d.pop("sourceEntityId", UNSET)

        transfer_quantity: Union[Unset, ContainerQuantity] = UNSET
        _transfer_quantity = d.pop("transferQuantity", UNSET)
        if not isinstance(_transfer_quantity, Unset):
            transfer_quantity = ContainerQuantity.from_dict(_transfer_quantity)

        container_transfer = cls(
            transfer_volume=transfer_volume,
            destination_contents=destination_contents,
            destination_quantity=destination_quantity,
            destination_volume=destination_volume,
            source_batch_id=source_batch_id,
            source_container_id=source_container_id,
            source_entity_id=source_entity_id,
            transfer_quantity=transfer_quantity,
        )

        return container_transfer

    @property
    def transfer_volume(self) -> ContainerVolume:
        return self._transfer_volume

    @transfer_volume.setter
    def transfer_volume(self, value: ContainerVolume) -> None:
        self._transfer_volume = value

    @property
    def destination_contents(self) -> List[ContainerTransferDestinationContentsItem]:
        if isinstance(self._destination_contents, Unset):
            raise NotPresentError(self, "destination_contents")
        return self._destination_contents

    @destination_contents.setter
    def destination_contents(self, value: List[ContainerTransferDestinationContentsItem]) -> None:
        self._destination_contents = value

    @destination_contents.deleter
    def destination_contents(self) -> None:
        self._destination_contents = UNSET

    @property
    def destination_quantity(self) -> ContainerQuantity:
        if isinstance(self._destination_quantity, Unset):
            raise NotPresentError(self, "destination_quantity")
        return self._destination_quantity

    @destination_quantity.setter
    def destination_quantity(self, value: ContainerQuantity) -> None:
        self._destination_quantity = value

    @destination_quantity.deleter
    def destination_quantity(self) -> None:
        self._destination_quantity = UNSET

    @property
    def destination_volume(self) -> ContainerVolume:
        if isinstance(self._destination_volume, Unset):
            raise NotPresentError(self, "destination_volume")
        return self._destination_volume

    @destination_volume.setter
    def destination_volume(self, value: ContainerVolume) -> None:
        self._destination_volume = value

    @destination_volume.deleter
    def destination_volume(self) -> None:
        self._destination_volume = UNSET

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
