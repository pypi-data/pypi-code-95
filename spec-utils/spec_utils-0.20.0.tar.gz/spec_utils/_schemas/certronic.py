from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime as dt

class Clocking(BaseModel):
    id: int
    center: str
    ss: str
    datetime: dt
    action: Optional[str] = None


class ClockingList(BaseModel):
    __root__: List[Clocking]