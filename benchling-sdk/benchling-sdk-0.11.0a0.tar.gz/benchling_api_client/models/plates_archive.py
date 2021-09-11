from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..models.plates_archive_reason import PlatesArchiveReason

T = TypeVar("T", bound="PlatesArchive")


@attr.s(auto_attribs=True, repr=False)
class PlatesArchive:
    """  """

    _plate_ids: List[str]
    _reason: PlatesArchiveReason
    _should_remove_barcodes: bool

    def __repr__(self):
        fields = []
        fields.append("plate_ids={}".format(repr(self._plate_ids)))
        fields.append("reason={}".format(repr(self._reason)))
        fields.append("should_remove_barcodes={}".format(repr(self._should_remove_barcodes)))
        return "PlatesArchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        plate_ids = self._plate_ids

        reason = self._reason.value

        should_remove_barcodes = self._should_remove_barcodes

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "plateIds": plate_ids,
                "reason": reason,
                "shouldRemoveBarcodes": should_remove_barcodes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        plate_ids = cast(List[str], d.pop("plateIds"))

        reason = PlatesArchiveReason(d.pop("reason"))

        should_remove_barcodes = d.pop("shouldRemoveBarcodes")

        plates_archive = cls(
            plate_ids=plate_ids,
            reason=reason,
            should_remove_barcodes=should_remove_barcodes,
        )

        return plates_archive

    @property
    def plate_ids(self) -> List[str]:
        return self._plate_ids

    @plate_ids.setter
    def plate_ids(self, value: List[str]) -> None:
        self._plate_ids = value

    @property
    def reason(self) -> PlatesArchiveReason:
        return self._reason

    @reason.setter
    def reason(self, value: PlatesArchiveReason) -> None:
        self._reason = value

    @property
    def should_remove_barcodes(self) -> bool:
        return self._should_remove_barcodes

    @should_remove_barcodes.setter
    def should_remove_barcodes(self, value: bool) -> None:
        self._should_remove_barcodes = value
