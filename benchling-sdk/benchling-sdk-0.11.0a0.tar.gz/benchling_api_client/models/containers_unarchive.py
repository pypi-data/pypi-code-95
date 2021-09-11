from typing import Any, cast, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="ContainersUnarchive")


@attr.s(auto_attribs=True, repr=False)
class ContainersUnarchive:
    """  """

    _container_ids: List[str]

    def __repr__(self):
        fields = []
        fields.append("container_ids={}".format(repr(self._container_ids)))
        return "ContainersUnarchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        container_ids = self._container_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "containerIds": container_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        container_ids = cast(List[str], d.pop("containerIds"))

        containers_unarchive = cls(
            container_ids=container_ids,
        )

        return containers_unarchive

    @property
    def container_ids(self) -> List[str]:
        return self._container_ids

    @container_ids.setter
    def container_ids(self, value: List[str]) -> None:
        self._container_ids = value
