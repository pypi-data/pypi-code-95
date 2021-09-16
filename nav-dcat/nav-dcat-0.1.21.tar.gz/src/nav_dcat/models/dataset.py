from typing import Optional, Sequence, List

from nav_dcat.models.access_groups import AccessGroups
from pydantic import BaseModel

from nav_dcat.fields import common_fields


class DatasetDocument(BaseModel):
    id: str
    title: str
    sources: Optional[List[str]] = []
    description: Optional[str] = ""
    modified: Optional[str] = None
    issued: Optional[str] = None
    spatial: Optional[str] = ""
    accessRights: Optional[common_fields.AccessRights] = common_fields.AccessRights.INTERNAL.value
    accessGroups: Optional[AccessGroups] = AccessGroups
    keyword: Optional[Sequence] = []
    url: Optional[str] = ""
