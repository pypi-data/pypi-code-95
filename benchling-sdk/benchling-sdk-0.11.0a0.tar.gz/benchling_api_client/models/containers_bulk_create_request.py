from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.container_create import ContainerCreate

T = TypeVar("T", bound="ContainersBulkCreateRequest")


@attr.s(auto_attribs=True, repr=False)
class ContainersBulkCreateRequest:
    """  """

    _containers: List[ContainerCreate]

    def __repr__(self):
        fields = []
        fields.append("containers={}".format(repr(self._containers)))
        return "ContainersBulkCreateRequest({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        containers = []
        for containers_item_data in self._containers:
            containers_item = containers_item_data.to_dict()

            containers.append(containers_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "containers": containers,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        containers = []
        _containers = d.pop("containers")
        for containers_item_data in _containers:
            containers_item = ContainerCreate.from_dict(containers_item_data)

            containers.append(containers_item)

        containers_bulk_create_request = cls(
            containers=containers,
        )

        return containers_bulk_create_request

    @property
    def containers(self) -> List[ContainerCreate]:
        return self._containers

    @containers.setter
    def containers(self, value: List[ContainerCreate]) -> None:
        self._containers = value
