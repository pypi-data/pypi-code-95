__all__ = [
    'BaseTable',
]

from abc import ABC, abstractmethod
from typing import Optional
from UniversalParser.html.output import parse_html_table
from UniversalParser._tools import *
from UniversalParser._parse import parse_xml
from UniversalParser._ntype import *
from UniversalParser.micro._ntype import *
from UniversalParser._exception import *
from UniversalParser.manager import ChainManager

class BaseTable(ABC):

    def __init__(self
            , zip_file_path: str
            , tag_type: str
            , read_file_path: Optional[str] = None
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
        super().__init__()
        self.zip_file_path = zip_file_path
        self.tag_type = tag_type
        self.file_path = read_file_path
        self.encoding = encoding
        self.mode = mode
        self.attr_prefix = attr_prefix
        self._analysis_text = analysis_text
        self.cdata_key = cdata_key
        self.real_cdata_key = real_cdata_key
        self.cdata_self_key = cdata_self_key
        self.comment_key = comment_key
        self.cdata_separator = cdata_separator
        self.analysis_mode = analysis_mode
        self.Tag = self.__get_tag_type(self.tag_type)
        self.tables = [] # all of tables.

        try:
            self.zip_obj = ZipFile(self.zip_file_path, mode=self.mode)
        except Exception as e:
            raise ZipParseError(f'zip-file can not be parsed.{e}')
        self._init_manager()
        self.refresh_tables()

    def _init_manager(self):
        self.ori_xml = read_content_from_zipobj(self.zip_obj, self.file_path, self.encoding)
        self.manager: ChainManager = parse_xml(
            self.ori_xml
            , analysis_text = self._analysis_text
            , attr_prefix = self.attr_prefix
            , cdata_key = self.cdata_key
            , real_cdata_key = self.real_cdata_key
            , cdata_self_key = self.cdata_self_key
            , comment_key = self.comment_key
            , cdata_separator = self.cdata_separator
            , analysis_mode = self.analysis_mode
        )

    @abstractmethod
    def refresh_tables(self): pass

    @abstractmethod
    def modify_cell_by_coordinate(self): pass

    @abstractmethod
    def batch_modify_cells_by_coordinate(self): pass

    def __get_tag_type(self, tag_type: str):
        if MicroTagType.WORD == tag_type:
            return WordTag
        elif MicroTagType.PPT == tag_type:
            return PowerPointTag
        elif MicroTagType.EXCEL == tag_type:
            return ExcelTag
        else:
            raise Exception('Unsupprot doc type.')

    def to_html(self
            , title: str = 'Table'
            , out_path: str = 'tables.html'
            , encoding: str = 'utf-8'
        ):
        with open(out_path, 'w', encoding=encoding) as fp:
            fp.write(parse_html_table(self.tables, title=title))

    def to_word(self): pass

    def to_pdf(self): pass        

    def to_excel(self): pass

    def save_as(self, new_word_path):
        new_xml_data = self.manager.get_xml_data()
        save_docs_with_modify_by_move(self.zip_obj, {self.file_path: new_xml_data}, new_word_path)

    def __del__(self):
        try:
            self.zip_obj.close()
        except:
            pass
