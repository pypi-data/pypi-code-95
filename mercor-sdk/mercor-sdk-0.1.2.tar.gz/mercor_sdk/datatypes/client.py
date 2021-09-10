from datetime import datetime, timezone
from typing import Callable, Optional

from pydantic import BaseModel


def _current_time():
    return datetime.now(timezone.utc).timestamp()


class ClientRequest(BaseModel):
    endpoint: str
    headers: dict
    data: Optional[dict] = None
    json_data: Optional[dict] = None

    @property
    def payload(self) -> dict:
        return {"headers": self.headers, "data": self.data, "json": self.json_data}


class ClientToken(BaseModel):
    access_token: str
    token_type: str
    expires_at: float

    def is_expired(self, current_time: Callable[[], float] = _current_time) -> bool:
        return bool(current_time() > self.expires_at)
