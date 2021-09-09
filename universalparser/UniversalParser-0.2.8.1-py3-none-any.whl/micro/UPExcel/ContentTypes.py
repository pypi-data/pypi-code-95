from typing import Type
from zipfile import ZipFile
from UniversalParser._tools import read_content_from_zipobj
import UniversalParser as UP
from .constant import ContentTypeOverride

class UPContentTypes:

    PATH = '[Content_Types].xml'

    def __init__(self, zip_obj: ZipFile) -> None:
        content = read_content_from_zipobj(zip_obj, self.PATH)
        self.manager = UP.parse_xml(content, analysis_text=False)

    def get_main_path(self) -> str:
        for content_type in ContentTypeOverride.MAIN:
            try:
                return self.manager.find_node_by_attrs(ContentType=content_type).PartName.strip('/')
            except:
                pass
        else:
            raise TypeError('Unsupport. Please contact the developer.')

    def get_app_path(self) -> str:
        for content_type in ContentTypeOverride.EXTENDED_PROPERTIES:
            try:
                return self.manager.find_node_by_attrs(ContentType=content_type).PartName.strip('/')
            except:
                pass
        else:
            raise TypeError('Unsupport. Please contact the developer.')

    def get_core_path(self) -> str:
        for content_type in ContentTypeOverride.CORE_PROPERTIES:
            try:
                return self.manager.find_node_by_attrs(ContentType=content_type).PartName.strip('/')
            except:
                pass
        else:
            raise TypeError('Unsupport. Please contact the developer.')

    def get_custom_path(self) -> str:
        for content_type in ContentTypeOverride.CUSTOM_PROPERTIES:
            try:
                return self.manager.find_node_by_attrs(ContentType=content_type).PartName.strip('/')
            except:
                pass
        else:
            raise TypeError('Unsupport. Please contact the developer.')

    def get_shareString_path(self) -> str:
        for content_type in ContentTypeOverride.SHAREDSTRINGS:
            try:
                return self.manager.find_node_by_attrs(ContentType=content_type).PartName.strip('/')
            except:
                pass
        else:
            raise TypeError('Unsupport. Please contact the developer.')
            
