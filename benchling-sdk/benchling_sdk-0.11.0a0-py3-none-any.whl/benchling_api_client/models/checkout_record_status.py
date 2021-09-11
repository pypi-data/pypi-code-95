from enum import Enum


class CheckoutRecordStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    CHECKED_OUT = "CHECKED_OUT"

    def __str__(self) -> str:
        return str(self.value)
