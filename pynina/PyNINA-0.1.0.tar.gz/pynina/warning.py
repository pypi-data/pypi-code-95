import datetime
from typing import Dict, Any, Optional

from .const import ReadOnlyClass, ENDPOINT_NINA_BASE


class Warning(metaclass=ReadOnlyClass):
    """Class to reflect a warning."""
    def __init__(self, data: Dict[str, Any]):
        """Initialize."""
        self.id: str = data["payload"]["id"]
        self.headline: str = data["payload"]["data"]["headline"]
        self.sent: str = data["sent"]
        self.start: Optional[str] = data.get("start", None)
        self.expires: Optional[str] = data.get("expires", None)

        self.raw: Dict[str, Any] = data

    def isValid(self) -> bool:
        """Test if warning is valid."""
        if self.expires is not None:
            currDate: datetime = datetime.datetime.now().timestamp()
            expiresDate = datetime.datetime.fromisoformat(self.expires).timestamp()
            return currDate < expiresDate
        return True

    def __repr__(self) -> str:
        return f"{self.id} ({self.sent}): {self.headline}"
