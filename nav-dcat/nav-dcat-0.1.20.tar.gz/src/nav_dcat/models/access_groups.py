from typing import Optional, List
from pydantic import BaseModel


class AccessGroups(BaseModel):
    canRead: Optional[List[str]] = []
    canRequest: Optional[List[str]] = []
