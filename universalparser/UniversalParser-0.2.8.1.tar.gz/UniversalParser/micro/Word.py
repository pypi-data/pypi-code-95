__all__ = [
    'parse_tables',
]

from typing import Any, Dict, Tuple
from UniversalParser._ntype import *
from UniversalParser.micro._ntype import *
from .BaseTable import *
from UniversalParser._tools import *

class WordTable(BaseTable):

    def __init__(self
            , zip_file_path: str
            , read_file_path: str = 'word/document.xml'
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
            , MicroTagType.WORD
            , read_file_path = read_file_path
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

    def refresh_tables(self):
        self.tables = []
        for w_tbl in self.manager.find_nodes_by_tag(
                self.Tag.TABLE
            ):
            table = []
            for w_tr in self.manager.find_nodes_with_ancestor(
                    w_tbl
                    , tag_ = self.Tag.TR
                ):
                row = []
                for w_tc in self.manager.find_nodes_with_ancestor(
                        w_tr
                        , tag_ = self.Tag.TC
                    ):
                    try:
                        row.append(
                            self.manager.find_text(
                                w_tc[self.Tag.P][self.Tag.R][self.Tag.TEXT]
                            )
                        )
                    except:
                        row.append('')
                table.append(row)
            self.tables.append(table)
        return self.tables

    def modify_cell_by_coordinate(self, table_loc: int, coordinate: Tuple[ROW, COL], new_value: Any) -> Any:
        row, col = coordinate
        try:
            table = self.manager.find_nodes_by_tag(self.Tag.TABLE)[table_loc-1]
            row_obj = self.manager.find_nodes_with_ancestor(table, tag_ = self.Tag.TR)[row-1]
            cell_obj = self.manager.find_nodes_with_ancestor(row_obj, tag_ = self.Tag.TC)[col-1]
            tag_P = cell_obj[self.Tag.P]
        except Exception as e:
            raise ZipParseError(f'Modify zip-file error.{e}')
        else:
            try: # MicroSoft Word 2010 will take apart illegal word. Combine them.
                old_value = self.manager.update_text(tag_P[self.Tag.R][self.Tag.TEXT], new_value)
            except: # Unfound
                old_value = ''
                tag_R = self.manager.insert(tag_P, self.Tag.R, {})
                tag_RPR = self.manager.insert(tag_R, self.Tag.RPR, {})
                self.manager.insert(tag_RPR, self.Tag.RFONTS, {self.Tag.Attribute.HINT: 'eastAsia'})
                self.manager.insert(tag_RPR, self.Tag.VERTALIGN, {self.Tag.Attribute.VAL: 'baseline'})
                self.manager.insert(tag_RPR, self.Tag.LANG, {self.Tag.Attribute.VAL: 'en-US', self.Tag.Attribute.EASTASIA: 'zh-CN'})
                self.manager.insert(tag_R, self.Tag.TEXT, {}, new_value)
            return old_value

    def batch_modify_cells_by_coordinate(self
            , table_loc: int
            , coordinate_values: Dict[Tuple[ROW, COL], Any]
        ) -> Dict[Tuple[ROW, COL], Any]:
        old_values = {}
        for coordinate, new_value in coordinate_values.items():
            old_values[coordinate] = self.modify_cell_by_coordinate(table_loc, coordinate, new_value)
        return old_values
    
    def save_from_modify(self, new_word_path: str='output.docx', patt=None, **kwargs):
        new_content = patt_template_replace(self.ori_xml, patt=patt, **kwargs)
        save_docs_with_modify_by_move(self.zip_obj, {self.file_path: new_content}, new_word_path)

    
def parse_tables(
        zip_file_path: str
        , read_file_path: str = 'word/document.xml'
        , encoding: str = 'utf-8'
        , attr_prefix: str = ATTR_PREFIX
        , cdata_key: str = CDATA_KEY
        , real_cdata_key: str = REAL_CDATA_KEY
        , cdata_self_key: str = CDATA_SELF_KEY
        , comment_key: str = COMMENT_KEY
        , analysis_text: bool = False
        , cdata_separator: str = CDATA_SEPARATOR
        , analysis_mode: int = AnalysisMode.RECURSION_OLD
    ) -> WordTable:
    return WordTable(
        zip_file_path = zip_file_path
        , read_file_path = read_file_path
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
