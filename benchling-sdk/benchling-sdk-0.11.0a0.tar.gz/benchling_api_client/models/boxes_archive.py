from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.boxes_archive_reason import BoxesArchiveReason
from ..types import UNSET, Unset

T = TypeVar("T", bound="BoxesArchive")


@attr.s(auto_attribs=True, repr=False)
class BoxesArchive:
    """  """

    _box_ids: List[str]
    _reason: BoxesArchiveReason
    _should_remove_barcodes: Union[Unset, bool] = UNSET

    def __repr__(self):
        fields = []
        fields.append("box_ids={}".format(repr(self._box_ids)))
        fields.append("reason={}".format(repr(self._reason)))
        fields.append("should_remove_barcodes={}".format(repr(self._should_remove_barcodes)))
        return "BoxesArchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        box_ids = self._box_ids

        reason = self._reason.value

        should_remove_barcodes = self._should_remove_barcodes

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "boxIds": box_ids,
                "reason": reason,
            }
        )
        if should_remove_barcodes is not UNSET:
            field_dict["shouldRemoveBarcodes"] = should_remove_barcodes

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        box_ids = cast(List[str], d.pop("boxIds"))

        reason = BoxesArchiveReason(d.pop("reason"))

        should_remove_barcodes = d.pop("shouldRemoveBarcodes", UNSET)

        boxes_archive = cls(
            box_ids=box_ids,
            reason=reason,
            should_remove_barcodes=should_remove_barcodes,
        )

        return boxes_archive

    @property
    def box_ids(self) -> List[str]:
        return self._box_ids

    @box_ids.setter
    def box_ids(self, value: List[str]) -> None:
        self._box_ids = value

    @property
    def reason(self) -> BoxesArchiveReason:
        return self._reason

    @reason.setter
    def reason(self, value: BoxesArchiveReason) -> None:
        self._reason = value

    @property
    def should_remove_barcodes(self) -> bool:
        if isinstance(self._should_remove_barcodes, Unset):
            raise NotPresentError(self, "should_remove_barcodes")
        return self._should_remove_barcodes

    @should_remove_barcodes.setter
    def should_remove_barcodes(self, value: bool) -> None:
        self._should_remove_barcodes = value

    @should_remove_barcodes.deleter
    def should_remove_barcodes(self) -> None:
        self._should_remove_barcodes = UNSET
