from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..models.entity_archive_reason import EntityArchiveReason

T = TypeVar("T", bound="MixturesArchive")


@attr.s(auto_attribs=True, repr=False)
class MixturesArchive:
    """The request body for archiving mixtures."""

    _mixture_ids: List[str]
    _reason: EntityArchiveReason

    def __repr__(self):
        fields = []
        fields.append("mixture_ids={}".format(repr(self._mixture_ids)))
        fields.append("reason={}".format(repr(self._reason)))
        return "MixturesArchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        mixture_ids = self._mixture_ids

        reason = self._reason.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "mixtureIds": mixture_ids,
                "reason": reason,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        mixture_ids = cast(List[str], d.pop("mixtureIds"))

        reason = EntityArchiveReason(d.pop("reason"))

        mixtures_archive = cls(
            mixture_ids=mixture_ids,
            reason=reason,
        )

        return mixtures_archive

    @property
    def mixture_ids(self) -> List[str]:
        return self._mixture_ids

    @mixture_ids.setter
    def mixture_ids(self, value: List[str]) -> None:
        self._mixture_ids = value

    @property
    def reason(self) -> EntityArchiveReason:
        return self._reason

    @reason.setter
    def reason(self, value: EntityArchiveReason) -> None:
        self._reason = value
