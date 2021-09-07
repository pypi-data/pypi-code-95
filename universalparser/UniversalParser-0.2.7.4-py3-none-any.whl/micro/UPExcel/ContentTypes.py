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
        return self.manager.find_node_by_attrs(
            ContentType=ContentTypeOverride.MAIN).PartName.strip('/')

    def get_app_path(self) -> str:
        return self.manager.find_node_by_attrs(
            ContentType=ContentTypeOverride.EXTENDED_PROPERTIES).PartName.strip('/')

    def get_core_path(self) -> str:
        return self.manager.find_node_by_attrs(
            ContentType=ContentTypeOverride.CORE_PROPERTIES).PartName.strip('/')

    def get_custom_path(self) -> str:
        return self.manager.find_node_by_attrs(
            ContentType=ContentTypeOverride.CUSTOM_PROPERTIES).PartName.strip('/')

    def get_shareString_path(self) -> str:
        return self.manager.find_node_by_attrs(
            ContentType=ContentTypeOverride.SHAREDSTRINGS).PartName.strip('/')
