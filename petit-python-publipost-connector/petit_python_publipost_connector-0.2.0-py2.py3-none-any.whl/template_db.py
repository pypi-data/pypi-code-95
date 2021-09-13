import io
import time
from dataclasses import dataclass
from typing import Dict, Generic, List, Optional, Type, TypeVar

from minio.api import Minio

from .datastructure import S3Path
from .engine import Template
from .utils import download_minio_stream

TemplateType = TypeVar('TemplateType', bound=Template)


@dataclass
class TemplateContainer(Generic[TemplateType]):
    templater: TemplateType
    pulled_at: float


class TemplateDB(Generic[TemplateType]):
    def __init__(self, template_class: Type[TemplateType]):
        self.__template_class = template_class
        self.__templates: Dict[str, TemplateContainer[TemplateType]] = {}
        # should use a better s3 interface
        self.__s3_client: Optional[Minio] = None

    def set_s3_client(self, client: Minio) -> None:
        self.__s3_client = client

    def render_template(self, exposed_as: str, data: dict, options: Optional[List[str]]) -> io.BytesIO:
        return self.__templates[exposed_as].templater.render(data, options)

    def delete_template(self, exposed_as:str) -> None:
        del self.__templates[exposed_as]

    def add_template(self, s3_path: S3Path, exposed_as: str) -> Template:
        doc = self.__s3_client.get_object(s3_path.bucket, s3_path.path)
        _file = io.BytesIO()
        download_minio_stream(doc, _file)
        template = self.__template_class(_file)
        self.__templates[exposed_as] = TemplateContainer(template, time.time())
        return template

    def get_fields(self, exposed_as: str) -> List[str]:
        return self.__templates[exposed_as].templater.fields

    def get_containers(self) -> Dict[str, TemplateContainer]:
        return self.__templates
