from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.locations_archive_reason import LocationsArchiveReason
from ..types import UNSET, Unset

T = TypeVar("T", bound="LocationsArchive")


@attr.s(auto_attribs=True, repr=False)
class LocationsArchive:
    """  """

    _location_ids: List[str]
    _reason: LocationsArchiveReason
    _should_remove_barcodes: Union[Unset, bool] = UNSET

    def __repr__(self):
        fields = []
        fields.append("location_ids={}".format(repr(self._location_ids)))
        fields.append("reason={}".format(repr(self._reason)))
        fields.append("should_remove_barcodes={}".format(repr(self._should_remove_barcodes)))
        return "LocationsArchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        location_ids = self._location_ids

        reason = self._reason.value

        should_remove_barcodes = self._should_remove_barcodes

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "locationIds": location_ids,
                "reason": reason,
            }
        )
        if should_remove_barcodes is not UNSET:
            field_dict["shouldRemoveBarcodes"] = should_remove_barcodes

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        location_ids = cast(List[str], d.pop("locationIds"))

        reason = LocationsArchiveReason(d.pop("reason"))

        should_remove_barcodes = d.pop("shouldRemoveBarcodes", UNSET)

        locations_archive = cls(
            location_ids=location_ids,
            reason=reason,
            should_remove_barcodes=should_remove_barcodes,
        )

        return locations_archive

    @property
    def location_ids(self) -> List[str]:
        return self._location_ids

    @location_ids.setter
    def location_ids(self, value: List[str]) -> None:
        self._location_ids = value

    @property
    def reason(self) -> LocationsArchiveReason:
        return self._reason

    @reason.setter
    def reason(self, value: LocationsArchiveReason) -> None:
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
