from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.mixture_update import MixtureUpdate
from ..types import UNSET, Unset

T = TypeVar("T", bound="MixturesBulkUpdate")


@attr.s(auto_attribs=True, repr=False)
class MixturesBulkUpdate:
    """  """

    _mixtures: Union[Unset, List[MixtureUpdate]] = UNSET

    def __repr__(self):
        fields = []
        fields.append("mixtures={}".format(repr(self._mixtures)))
        return "MixturesBulkUpdate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        mixtures: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._mixtures, Unset):
            mixtures = []
            for mixtures_item_data in self._mixtures:
                mixtures_item = mixtures_item_data.to_dict()

                mixtures.append(mixtures_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if mixtures is not UNSET:
            field_dict["mixtures"] = mixtures

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        mixtures = []
        _mixtures = d.pop("mixtures", UNSET)
        for mixtures_item_data in _mixtures or []:
            mixtures_item = MixtureUpdate.from_dict(mixtures_item_data)

            mixtures.append(mixtures_item)

        mixtures_bulk_update = cls(
            mixtures=mixtures,
        )

        return mixtures_bulk_update

    @property
    def mixtures(self) -> List[MixtureUpdate]:
        if isinstance(self._mixtures, Unset):
            raise NotPresentError(self, "mixtures")
        return self._mixtures

    @mixtures.setter
    def mixtures(self, value: List[MixtureUpdate]) -> None:
        self._mixtures = value

    @mixtures.deleter
    def mixtures(self) -> None:
        self._mixtures = UNSET
