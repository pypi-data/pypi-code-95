from enum import Enum


class BlobUploadStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"
    ABORTED = "ABORTED"

    def __str__(self) -> str:
        return str(self.value)
