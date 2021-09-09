__all__ = [
    'parse_tables',
]

from .BaseTable import *
from UniversalParser._ntype import *
from UniversalParser.micro._ntype import *

class ExcelTable(BaseTable):
    
    def __init__(self
            , zip_file_path: str
            , read_file_path: str = 'ppt/slides/slide1.xml'
            , encoding: str = 'utf-8'
            , mode: str = 'a' # do not use `w` mode, remember!
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
            , MicroTagType.PPT
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

    def refresh_tables(self): pass

    def modify_cell_by_coordinate(self): pass

    def batch_modify_cells_by_coordinate(self): pass

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
    read_file_path: str = f'ppt/slides/slide1.xml'
    return ExcelTable(
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
