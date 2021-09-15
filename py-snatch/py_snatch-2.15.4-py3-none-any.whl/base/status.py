from enum import Enum, unique


@unique
class IntegrationStatus(Enum):
    NOT_FOUND = "NOT_FOUND"
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    EXPIRED = "EXPIRED"
    SUCCESS = "SUCCESS"
    NO_DATA = "NO_DATA"
    INCOMPLETE = "INCOMPLETE"
    ERROR = "ERROR"
    CONN_ERROR = "CONN_ERROR"
    TIMEOUT = "TIMEOUT"

    def __str__(self):
        """Return Enum value for string operations."""
        return self.value

    def __eq__(self, other):
        """Compare objects using value or string."""
        if isinstance(other, str):
            return self.value == other
        return self.value == other.value

    @property
    def is_final(self) -> bool:
        """Return if data is final.

        No more requests to backend is need.

        """
        return self.is_success or self.is_failure

    @property
    def need_wait(self) -> bool:
        """Return if data still need response from backend."""
        return self.value in ["PENDING", "RUNNING", "WAITING"]

    @property
    def is_success(self) -> bool:
        """Return if Backend request is successful."""
        return self.value in ["SUCCESS", "NO_DATA", "INCOMPLETE"]

    @property
    def is_failure(self) -> bool:
        """Return if Backend request was a failure.

        `ERROR`, `EXPIRED`, and `NOT_FOUND` are not here, because
        these status were not final. They will start a new
        request to Backend.

        """
        return self.value in ["CONN_ERROR", "TIMEOUT"]
