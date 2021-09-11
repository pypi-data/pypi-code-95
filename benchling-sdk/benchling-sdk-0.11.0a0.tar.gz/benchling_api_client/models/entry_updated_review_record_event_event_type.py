from enum import Enum


class EntryUpdatedReviewRecordEventEventType(str, Enum):
    V2_ENTRYUPDATEDREVIEWRECORD = "v2.entry.updated.reviewRecord"

    def __str__(self) -> str:
        return str(self.value)
