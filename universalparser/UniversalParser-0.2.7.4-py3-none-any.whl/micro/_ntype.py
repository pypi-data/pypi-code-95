from typing import TypeVar

# table
ROW = TypeVar('ROW')
COL = TypeVar('COL')

class MicroTagType:
    WORD = 'word'
    EXCEL = 'excel'
    PPT = 'ppt'

class WordTag:
    TABLE = 'w:tbl'
    TR = 'w:tr'
    TC = 'w:tc'
    P = 'w:p'
    R = 'w:r'
    TEXT = 'w:t'
    TCPR = 'w:tcPr'
    RPR = 'w:rPr'
    RFONTS = 'w:rFonts'
    VERTALIGN = 'w:vertAlign'
    LANG = 'w:lang'

    class Attribute:
        GRIDSPAN = 'w:gridSpan' # w:val="2" [combine cols]
        VMERGE = 'w:vMerge' # w:val="restart"  w:val="continue" [combine rows]
        VAL = 'w:val'
        HINT = 'w:hint'
        EASTASIA = 'w:eastAsia'

class PowerPointTag:
    TABLE = 'a:tbl'
    TR = 'a:tr'
    TC = 'a:tc'
    P = 'a:p'
    R = 'a:r'
    TEXT = 'a:t'
    
    class Attribute:
        pass

class ExcelTag:
    TABLE = 'sheetData'
    TR = 'row'
    TC = 'c'
    TEXT = 'v'

    class Attribute:
        LOC = 'r'
        SPANS = 'spans'
