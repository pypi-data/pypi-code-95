from typing import Optional, Sequence, Union, List
from datetime import date
from pydantic import BaseModel

from nav_dcat.fields import common_fields


class ESDocument(BaseModel):
    id: str
    title: str
    description: str
    type: common_fields.Type
    uri: str
    format: Optional[Union[common_fields.Type, List[common_fields.Type]]]
    modified: Optional[str] = None
    issued: Optional[str] = None
    periodicity: Optional[str] = ""
    provenance: Optional[str] = "NAV"
    contactPoint: Optional[dict] = {}
    author: Optional[str] = ""
    repo: Optional[str] = ""
    readme: Optional[str] = ""
    spatial: Optional[Union[str, List[str]]] = ""
    accessRights: Optional[common_fields.AccessRights] = common_fields.AccessRights.INTERNAL.value
    pii: Optional[common_fields.Pii] = common_fields.Pii.FALSE.value
    keyword: Optional[Sequence] = []
    theme: Optional[Union[str, List[str]]] = ""
    temporal: Optional[dict] = {"from": f"{date.today().year}", "to": f"{date.today().year}"}
    language: Optional[str] = "NO"
    creator: Optional[dict] = {}
    publisher: Optional[dict] = {"name": "NAV"}
    license: Optional[dict] = {}
    rights: Optional[str] = f"Copyright {date.today().year}, NAV"
    content: Optional[dict] = {}
    url: Optional[str] = ""
    master: Optional[str] = ""

