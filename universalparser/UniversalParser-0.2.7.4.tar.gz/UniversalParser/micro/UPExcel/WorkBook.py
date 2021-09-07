from typing import Dict, List
from zipfile import ZipFile
from UniversalParser._tools import read_content_from_zipobj
import UniversalParser as UP
from .ContentTypes import UPContentTypes
from .Sheet import UPSheet

class UPWorkBook:

    def __init__(self, excel_path: str, mode: str = 'a') -> None:

        self.zip_obj = ZipFile(excel_path, mode=mode)

        self.contentTypes = UPContentTypes(self.zip_obj) # 全部的XML路径类型名称对照表

        self.main_path = self.contentTypes.get_main_path().split('/')

        self.Relationship: Dict[str, str] = {}
        self._init_Relationship()

        self._sis: List[str] = [] # 中文对照表
        try:
            self._init_sharedString()
        except:
            pass

        self.sheets: List[UPSheet] = []
        self._init_sheets()
    
    def _init_Relationship(self) -> None:
        p_dir = '/'.join(self.main_path[:-1])
        main_file_name = self.main_path[-1]
        _rels_path: str = f"{p_dir}/_rels/{main_file_name}.rels"
        content = read_content_from_zipobj(self.zip_obj, _rels_path)
        rels_manager = UP.parse_xml(content, analysis_text=False)
        for _r in rels_manager.find_nodes_by_tag('Relationship'):
            self.Relationship[_r.Id] = f"{p_dir}/{_r.Target}" # whole
            
    def _init_sharedString(self):
        shareString_path = self.contentTypes.get_shareString_path()
        content = read_content_from_zipobj(self.zip_obj, shareString_path)
        manager = UP.parse_xml(content, analysis_text=False)
        for _ in manager.find_nodes_by_tag('si'):
            self._sis.append(_.t)

    def _init_sheets(self):
        content = read_content_from_zipobj(self.zip_obj, '/'.join(self.main_path))
        manager = UP.parse_xml(content, analysis_text=False)
        for sheet in manager.find_nodes_by_tag('sheet'):
            sheet_path = self.Relationship[sheet['r:id']]
            self.sheets.append(
                UPSheet(sheet.name, sheet.sheetId, sheet['r:id'], self.zip_obj, sheet_path, self._sis)
            )

    def __del__(self):
        try:
            self.zip_obj.close()
        except:
            pass