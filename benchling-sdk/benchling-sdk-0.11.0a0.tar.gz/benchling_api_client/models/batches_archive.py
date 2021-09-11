from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..models.batches_archive_reason import BatchesArchiveReason

T = TypeVar("T", bound="BatchesArchive")


@attr.s(auto_attribs=True, repr=False)
class BatchesArchive:
    """The request body for archiving Batches."""

    _batch_ids: List[str]
    _reason: BatchesArchiveReason

    def __repr__(self):
        fields = []
        fields.append("batch_ids={}".format(repr(self._batch_ids)))
        fields.append("reason={}".format(repr(self._reason)))
        return "BatchesArchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        batch_ids = self._batch_ids

        reason = self._reason.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "batchIds": batch_ids,
                "reason": reason,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        batch_ids = cast(List[str], d.pop("batchIds"))

        reason = BatchesArchiveReason(d.pop("reason"))

        batches_archive = cls(
            batch_ids=batch_ids,
            reason=reason,
        )

        return batches_archive

    @property
    def batch_ids(self) -> List[str]:
        return self._batch_ids

    @batch_ids.setter
    def batch_ids(self, value: List[str]) -> None:
        self._batch_ids = value

    @property
    def reason(self) -> BatchesArchiveReason:
        return self._reason

    @reason.setter
    def reason(self, value: BatchesArchiveReason) -> None:
        self._reason = value
