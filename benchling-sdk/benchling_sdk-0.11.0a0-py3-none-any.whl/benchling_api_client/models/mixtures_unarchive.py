from typing import Any, cast, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="MixturesUnarchive")


@attr.s(auto_attribs=True, repr=False)
class MixturesUnarchive:
    """The request body for unarchiving mixtures."""

    _mixture_ids: List[str]

    def __repr__(self):
        fields = []
        fields.append("mixture_ids={}".format(repr(self._mixture_ids)))
        return "MixturesUnarchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        mixture_ids = self._mixture_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "mixtureIds": mixture_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        mixture_ids = cast(List[str], d.pop("mixtureIds"))

        mixtures_unarchive = cls(
            mixture_ids=mixture_ids,
        )

        return mixtures_unarchive

    @property
    def mixture_ids(self) -> List[str]:
        return self._mixture_ids

    @mixture_ids.setter
    def mixture_ids(self, value: List[str]) -> None:
        self._mixture_ids = value
