from typing import TypeVar, Union

class TextType:
    STR = 0
    INT = 1
    FLOAT = 2
    DECIMAL = 3

class ParserType:
    XML = 0
    JSON = 1
    DICT = 2
    YAML = 3
    HTML = 4

class AnalysisMode:
    RECURSION_OLD = 0
    RECOMMEND = 1
    DIRECT = 2

class SM:
    text = 0
    attr_names = 1
    tag = 2
    ancestor = 3
    descendants = 4
    siblings = 5
    children = 6
    parent = 7

Type_Path = TypeVar('Type_Path')
Type_JSON = Union[Type_Path, str]

# analysis area.
ATTR_PREFIX = '@'
CDATA_KEY = '#text'
REAL_CDATA_KEY = 'text_'
CDATA_SELF_KEY = '#CDATA'
COMMENT_KEY = '#comment'
LOC_KEY = '__loc__'
CDATA_SEPARATOR = ' '
