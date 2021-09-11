from enum import Enum


class ListEntriesReviewStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    RETRACTED = "RETRACTED"

    def __str__(self) -> str:
        return str(self.value)
