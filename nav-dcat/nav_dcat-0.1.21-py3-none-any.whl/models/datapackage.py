from typing import Optional, Sequence, Union, List
from pydantic import BaseModel

from nav_dcat.fields import common_fields


class DatapackageDocument(BaseModel):
    title: str
    description: str
    uri: Optional[str] = ""
    modified: Optional[str] = None
    issued: Optional[str] = None
    periodicity: Optional[str] = ""
    provenance: Optional[str] = "NAV"
    contactPoint: Optional[dict] = {}
    author: Optional[str] = ""
    repo: Optional[str] = ""
    readme: Optional[str] = ""
    spatial: Optional[str] = ""
    accessRights: Optional[common_fields.AccessRights] = common_fields.AccessRights.INTERNAL.value
    pii: Optional[common_fields.Pii] = common_fields.Pii.FALSE.value
    keyword: Optional[Sequence] = []
    theme: Optional[Union[str, List[str]]] = ""
    temporal: Optional[dict] = None
    language: Optional[str] = "NO"
    creator: Optional[dict] = {}
    publisher: Optional[dict] = {"name": "NAV"}
    license: Optional[dict] = {}
    rights: Optional[str] = None
    content: Optional[dict] = {}
    url: Optional[str] = ""
    resources: Optional[List[dict]] = []
    views: Optional[List[dict]] = []


class DPESDocument(BaseModel):
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
    spatial: Optional[str] = ""
    accessRights: Optional[common_fields.AccessRights] = common_fields.AccessRights.INTERNAL.value
    pii: Optional[common_fields.Pii] = common_fields.Pii.FALSE.value
    keyword: Optional[Sequence] = []
    theme: Optional[Union[str, List[str]]] = ""
    temporal: Optional[dict] = None
    language: Optional[str] = "NO"
    creator: Optional[dict] = {}
    publisher: Optional[dict] = {"name": "NAV"}
    license: Optional[dict] = {}
    rights: Optional[str] = None
    content: Optional[dict] = {}
    url: Optional[str] = ""
    resources: Optional[List[dict]] = []
    views: Optional[List[dict]] = []
