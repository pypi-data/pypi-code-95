__all__ = [
    'parse_tables',
]

from typing import Any
import re
from .BaseTable import *
from UniversalParser._tools import *
from UniversalParser._parse import parse_xml
from UniversalParser._ntype import *
from UniversalParser.micro._ntype import *
from UniversalParser.manager import ChainManager

class ExcelTable(BaseTable):
    
    def __init__(self
            , zip_file_path: str
            , encoding: str = 'utf-8'
            , mode: str = 'a'
            , attr_prefix: str = ATTR_PREFIX
            , cdata_key: str = CDATA_KEY
            , real_cdata_key: str = REAL_CDATA_KEY
            , cdata_self_key: str = CDATA_SELF_KEY
            , comment_key: str = COMMENT_KEY
            , analysis_text: bool = False
            , cdata_separator: str = CDATA_SEPARATOR
            , analysis_mode: int = AnalysisMode.RECURSION_OLD
        ) -> None:

        super().__init__(zip_file_path
            , MicroTagType.EXCEL
            , encoding = encoding
            , mode = mode
            , analysis_text = analysis_text
            , attr_prefix = attr_prefix
            , cdata_key = cdata_key
            , real_cdata_key = real_cdata_key
            , cdata_self_key = cdata_self_key
            , comment_key = comment_key
            , cdata_separator = cdata_separator
            , analysis_mode = analysis_mode
        )

    def _init_manager(self):
        self.ori_xmls = []
        self.managers: List[ChainManager] = []
        self.file_paths = []
        for info in self.zip_obj.infolist():
            sp_filename = info.filename.split('/')
            if not info.is_dir() and 3==len(sp_filename) and ['xl', 'worksheets']==sp_filename[:2] and sp_filename[2].endswith('.xml'):
                self.file_paths.append(info.filename)
        self.file_paths.sort(key=lambda x: x.replace('sheet','').replace('.xml',''), reverse=False)
        for filename in self.file_paths:
            ori_xml = read_content_from_zipobj(self.zip_obj, filename, self.encoding)
            self.ori_xmls.append(ori_xml)
            self.managers.append(parse_xml(
                ori_xml
                , analysis_text = self._analysis_text
                , attr_prefix = self.attr_prefix
                , cdata_key = self.cdata_key
                , real_cdata_key = self.real_cdata_key
                , cdata_self_key = self.cdata_self_key
                , comment_key = self.comment_key
                , cdata_separator = self.cdata_separator
                , analysis_mode = self.analysis_mode
            ))

    def refresh_tables(self): pass

    def modify_cell_by_coordinate(self, sheet_number: int, coordinate: str, new_value: Any) -> str:
        manager: ChainManager = self.managers[sheet_number-1]
        try:
            node = manager.find_node_by_attrs(**{self.Tag.Attribute.LOC: coordinate})
        except:
            patt_r = re.match(r'^([A-Z]+)([0-9]+)$', coordinate)
            if patt_r:
                col = patt_r.group(1)
                row = str(patt_r.group(2))
                try:
                    row_node = manager.find_nodes_by_tag_and_attrs(tag_=self.Tag.TR, **{self.Tag.Attribute.LOC:row})
                except:
                    table_node = manager.find_nodes_by_tag(self.Tag.TABLE, one_=True)
                    row_node = manager.insert(table_node, 'row', **{})
                
            else:
                raise ExcelCellLocError('Unable to locate excel cell.')
        return manager.update_text(node[self.Tag.TEXT], new_value)

    def batch_modify_cells_by_coordinate(self, sheet_number: int, coordinate_values: Dict[str, Any]) -> List[str]:
        old_values = []
        for coordinate, new_value in coordinate_values.items():
            old_values.append(self.modify_cell_by_coordinate(sheet_number, coordinate, new_value))
        return old_values

    def save_as(self, new_word_path):
        struct_datas = {self.file_paths[_1]:self.managers[_1].get_xml_data() for _1 in range(len(self.file_paths))}
        save_docs_with_modify_by_move(self.zip_obj, struct_datas, new_word_path)

def parse_tables(
        zip_file_path: str
        , encoding: str = 'utf-8'
        , attr_prefix: str = ATTR_PREFIX
        , cdata_key: str = CDATA_KEY
        , real_cdata_key: str = REAL_CDATA_KEY
        , cdata_self_key: str = CDATA_SELF_KEY
        , comment_key: str = COMMENT_KEY
        , analysis_text: bool = False
        , cdata_separator: str = CDATA_SEPARATOR
        , analysis_mode: int = AnalysisMode.RECURSION_OLD
    ) -> ExcelTable:

    return ExcelTable(
        zip_file_path = zip_file_path
        , encoding = encoding
        , attr_prefix = attr_prefix
        , cdata_key = cdata_key
        , real_cdata_key = real_cdata_key
        , cdata_self_key = cdata_self_key
        , comment_key = comment_key
        , analysis_text = analysis_text
        , cdata_separator = cdata_separator
        , analysis_mode = analysis_mode
    )
