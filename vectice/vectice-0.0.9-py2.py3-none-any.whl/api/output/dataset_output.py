from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from vectice.models import dataset


@dataclass
class __Output:
    id: int
    pattern: str
    isPatternBase: str
    creationDate: datetime
    updateDate: datetime
    deleteDate: Optional[datetime]
    isDeleted: str
    connectionId: int
    createdByUserId: int
    projectId: int
    workspaceId: int


@dataclass
class DatasetOutput(dataset.Dataset, __Output):
    pass
