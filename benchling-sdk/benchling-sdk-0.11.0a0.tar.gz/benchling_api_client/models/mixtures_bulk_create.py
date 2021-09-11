from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.mixture_create import MixtureCreate

T = TypeVar("T", bound="MixturesBulkCreate")


@attr.s(auto_attribs=True, repr=False)
class MixturesBulkCreate:
    """  """

    _mixtures: List[MixtureCreate]

    def __repr__(self):
        fields = []
        fields.append("mixtures={}".format(repr(self._mixtures)))
        return "MixturesBulkCreate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        mixtures = []
        for mixtures_item_data in self._mixtures:
            mixtures_item = mixtures_item_data.to_dict()

            mixtures.append(mixtures_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "mixtures": mixtures,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        mixtures = []
        _mixtures = d.pop("mixtures")
        for mixtures_item_data in _mixtures:
            mixtures_item = MixtureCreate.from_dict(mixtures_item_data)

            mixtures.append(mixtures_item)

        mixtures_bulk_create = cls(
            mixtures=mixtures,
        )

        return mixtures_bulk_create

    @property
    def mixtures(self) -> List[MixtureCreate]:
        return self._mixtures

    @mixtures.setter
    def mixtures(self, value: List[MixtureCreate]) -> None:
        self._mixtures = value
