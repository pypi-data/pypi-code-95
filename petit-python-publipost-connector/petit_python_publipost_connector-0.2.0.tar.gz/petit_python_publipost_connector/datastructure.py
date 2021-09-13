from dataclasses import dataclass
from typing import Any, List, Optional

from minio.api import Minio
from pydantic import BaseModel


class MinioCnfigure(BaseModel):
    host: str
    access_key: str
    pass_key: str
    secure: bool


class LoadTemplateBody(BaseModel):
    exposed_as: str
    bucket_name: str
    template_name: str


class PublipostBody(BaseModel):
    template_name: str
    r_template_name: str
    bucket_name: str
    output_name: str
    output_bucket: str
    data: Any
    options: Optional[List[str]]
    push_result: Any


@dataclass
class GlobalContext:
    s3_client: Optional[Minio] = None


@dataclass
class S3Path:
    bucket: str
    path: str
