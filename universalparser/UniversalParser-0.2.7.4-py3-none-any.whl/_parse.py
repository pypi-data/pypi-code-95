from .manager import ChainManager
from ._ntype import *
import os
from typing import Any, Dict

__all__ = [
    'parse',
    'parse_xml',
    'parse_json',
    'parse_dict',
    'parse_yaml',
    'parse_html_or_xhtml'
]

def parse_xml(
        xml_data: str
        , namespace_separator: str = None
        , attr_prefix: str = ATTR_PREFIX
        , cdata_key: str = CDATA_KEY
        , real_cdata_key: str = REAL_CDATA_KEY
        , cdata_self_key: str = CDATA_SELF_KEY
        , comment_key: str = COMMENT_KEY
        , analysis_text: bool = True
        , open_cdata: bool = False
        , open_comment: bool = False
        , cdata_separator: str = CDATA_SEPARATOR
        , analysis_mode: int = AnalysisMode.RECOMMEND
        , combine_cdata: bool = True
        , include_comment: bool = False
        , include_loc: bool = True
    ) -> ChainManager:
    return ChainManager(
        xml_data
        , attr_prefix = attr_prefix
        , cdata_key = cdata_key
        , real_cdata_key = real_cdata_key
        , cdata_self_key = cdata_self_key
        , comment_key = comment_key
        , analysis_text = analysis_text
        , cdata_separator = cdata_separator
        , analysis_mode = analysis_mode
        , combine_cdata = combine_cdata
        , include_comment = include_comment
        , include_loc = include_loc
        , open_cdata = open_cdata
        , open_comment = open_comment
        , namespace_separator = namespace_separator
    )

def parse(
        xml_path: str
        , namespace_separator: str = None
        , attr_prefix: str = ATTR_PREFIX
        , cdata_key: str = CDATA_KEY
        , real_cdata_key: str = REAL_CDATA_KEY
        , cdata_self_key: str = CDATA_SELF_KEY
        , comment_key: str = COMMENT_KEY
        , encoding: str = 'utf-8'
        , analysis_text: bool = True
        , open_cdata: bool = False
        , open_comment: bool = False
        , cdata_separator: str = CDATA_SEPARATOR
        , analysis_mode: int = AnalysisMode.RECOMMEND
        , combine_cdata: bool = True
        , include_comment: bool = False
        , include_loc: bool = True
    ) -> ChainManager:
    with open(xml_path, 'r', encoding=encoding) as fp:
        xml_data = fp.read()

    return parse_xml(
        xml_data
        , attr_prefix = attr_prefix
        , cdata_key = cdata_key
        , real_cdata_key = real_cdata_key
        , cdata_self_key = cdata_self_key
        , comment_key = comment_key
        , analysis_text = analysis_text
        , cdata_separator = cdata_separator
        , analysis_mode = analysis_mode
        , combine_cdata = combine_cdata
        , include_comment = include_comment
        , include_loc = include_loc
        , open_cdata = open_cdata
        , open_comment = open_comment
        , namespace_separator = namespace_separator
    )

def parse_json(
        json_data: str
        , attr_prefix: str = ATTR_PREFIX
        , cdata_key: str = CDATA_KEY
        , real_cdata_key: str = REAL_CDATA_KEY
        , analysis_text: bool = True
        , analysis_mode: int = AnalysisMode.RECURSION_OLD
    ) -> ChainManager:

    # if os.path.exists(json_data) and os.path.isfile(json_data):
    #     with open(json_data, 'r', encoding=encoding) as fp:
    #         json_data = fp.read()

    return ChainManager(
        ''
        , attr_prefix = attr_prefix
        , cdata_key = cdata_key
        , real_cdata_key = real_cdata_key
        , data_switch = ParserType.JSON
        , universal_data = json_data
        , analysis_text = analysis_text
        , analysis_mode = analysis_mode
    )

def parse_yaml(
        yaml_data: str
        , encoding='utf-8'
        , attr_prefix: str = ATTR_PREFIX
        , cdata_key: str = CDATA_KEY
        , real_cdata_key: str = REAL_CDATA_KEY
        , analysis_text: bool = True
        , analysis_mode: int = AnalysisMode.RECURSION_OLD
    ) -> ChainManager:

    if os.path.exists(yaml_data) and os.path.isfile(yaml_data):
        with open(yaml_data, 'r', encoding=encoding) as fp:
            yaml_data = fp.read()

    return ChainManager(
        ''
        , attr_prefix = attr_prefix
        , cdata_key = cdata_key
        , real_cdata_key = real_cdata_key
        , data_switch = ParserType.YAML
        , universal_data = yaml_data
        , analysis_text = analysis_text
        , analysis_mode = analysis_mode
    )

def parse_dict(
        dict_data: Dict[str, Any]
        , attr_prefix: str = ATTR_PREFIX
        , cdata_key: str = CDATA_KEY
        , real_cdata_key: str = REAL_CDATA_KEY
        , analysis_text: bool = True
        , analysis_mode: int = AnalysisMode.RECURSION_OLD
    ) -> ChainManager:
    return ChainManager(
        ''
        , attr_prefix = attr_prefix
        , cdata_key = cdata_key
        , real_cdata_key = real_cdata_key
        , data_switch = ParserType.DICT
        , universal_data = dict_data
        , analysis_text = analysis_text
        , analysis_mode = analysis_mode
    )

def parse_html_or_xhtml(html_data: str
        , convert_charrefs: bool = True
        , attr_prefix: str = ATTR_PREFIX
        , cdata_key: str = CDATA_KEY
        , comment_key: str = COMMENT_KEY
        , include_comment: bool = False
        , open_comment: bool = False
        , cdata_separator: str = CDATA_SEPARATOR
        , loc_key: str = LOC_KEY
        , include_loc: bool = True
        , analysis_text: bool = True
        , analysis_mode: int = AnalysisMode.RECOMMEND
    ) -> ChainManager:
    
    return ChainManager(
        ''
        , data_switch = ParserType.HTML
        , universal_data = html_data
        , convert_charrefs = convert_charrefs
        , attr_prefix = attr_prefix
        , cdata_key = cdata_key
        , comment_key = comment_key
        , include_comment = include_comment
        , cdata_separator = cdata_separator
        , loc_key = loc_key
        , include_loc = include_loc
        , analysis_text = analysis_text
        , analysis_mode = analysis_mode
        , open_comment = open_comment
    )
