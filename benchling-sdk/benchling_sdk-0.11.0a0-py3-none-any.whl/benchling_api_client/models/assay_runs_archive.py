from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..models.assay_runs_archive_reason import AssayRunsArchiveReason

T = TypeVar("T", bound="AssayRunsArchive")


@attr.s(auto_attribs=True, repr=False)
class AssayRunsArchive:
    """The request body for archiving Assay Runs."""

    _assay_run_ids: List[str]
    _reason: AssayRunsArchiveReason

    def __repr__(self):
        fields = []
        fields.append("assay_run_ids={}".format(repr(self._assay_run_ids)))
        fields.append("reason={}".format(repr(self._reason)))
        return "AssayRunsArchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        assay_run_ids = self._assay_run_ids

        reason = self._reason.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "assayRunIds": assay_run_ids,
                "reason": reason,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        assay_run_ids = cast(List[str], d.pop("assayRunIds"))

        reason = AssayRunsArchiveReason(d.pop("reason"))

        assay_runs_archive = cls(
            assay_run_ids=assay_run_ids,
            reason=reason,
        )

        return assay_runs_archive

    @property
    def assay_run_ids(self) -> List[str]:
        return self._assay_run_ids

    @assay_run_ids.setter
    def assay_run_ids(self, value: List[str]) -> None:
        self._assay_run_ids = value

    @property
    def reason(self) -> AssayRunsArchiveReason:
        return self._reason

    @reason.setter
    def reason(self, value: AssayRunsArchiveReason) -> None:
        self._reason = value
