# ------------------------------------------------------------ Imports ----------------------------------------------------------- #

# System
from typing import Dict, Optional, Union
from enum import Enum

# Local
from .file_key import FileKey
from .file_value import FileValue
from .file_consts import FileConsts

# -------------------------------------------------------------------------------------------------------------------------------- #



# -------------------------------------------------------- Public methods -------------------------------------------------------- #

def multi_replace(
    s: str,
    file_consts: FileConsts,
    keys_vals: Optional[Dict[FileKey, str]] = None,
    tab_size: Optional[int] = None,
    comment_line_len: Optional[int] = None
) -> str:
    keys_vals = keys_vals or {}

    if tab_size and comment_line_len:
        keys_vals.update({
            FileKey.COMMENT_LINE_INIT:                 comment_line(FileValue.COMMENT_LINE_INIT, comment_line_len, file_consts, tabs=1, tab_size=tab_size),
            FileKey.COMMENT_LINE_OVERRIDES:            comment_line(FileValue.COMMENT_LINE_OVERRIDES, comment_line_len, file_consts, tabs=1, tab_size=tab_size),
            FileKey.COMMENT_LINE_PUBLIC_PROPERTIES:    comment_line(FileValue.COMMENT_LINE_PUBLIC_PROPERTIES, comment_line_len, file_consts, tabs=1, tab_size=tab_size),
            FileKey.COMMENT_LINE_PUBLIC_METHODS:       comment_line(FileValue.COMMENT_LINE_PUBLIC_METHODS, comment_line_len, file_consts, tabs=1, tab_size=tab_size),
            FileKey.COMMENT_LINE_PRIVATE_PROPERTIES:   comment_line(FileValue.COMMENT_LINE_PRIVATE_PROPERTIES, comment_line_len, file_consts, tabs=1, tab_size=tab_size),
            FileKey.COMMENT_LINE_PRIVATE_METHODS:      comment_line(FileValue.COMMENT_LINE_PRIVATE_METHODS, comment_line_len, file_consts, tabs=1, tab_size=tab_size),
            FileKey.COMMENT_LINE_IMPORTS:              comment_line(FileValue.COMMENT_LINE_IMPORTS, comment_line_len, file_consts),
            FileKey.COMMENT_LINE_PUBLIC_VARS:          comment_line(FileValue.COMMENT_LINE_PUBLIC_VARS, comment_line_len, file_consts),
            FileKey.COMMENT_LINE_FILE_PUBLIC_METHODS:  comment_line(FileValue.COMMENT_LINE_PUBLIC_METHODS, comment_line_len, file_consts),
            FileKey.COMMENT_LINE_PRIVATE_VARS:         comment_line(FileValue.COMMENT_LINE_PRIVATE_VARS, comment_line_len, file_consts),
            FileKey.COMMENT_LINE_FILE_PRIVATE_METHODS: comment_line(FileValue.COMMENT_LINE_PRIVATE_METHODS, comment_line_len, file_consts),
            FileKey.COMMENT_LINE_METHODS:              comment_line(FileValue.COMMENT_LINE_METHODS, comment_line_len, file_consts),
            FileKey.COMMENT_LINE_PATHS:                comment_line(FileValue.COMMENT_LINE_PATHS, comment_line_len, file_consts),
            FileKey.COMMENT_LINE_VARS:                 comment_line(FileValue.COMMENT_LINE_VARS, comment_line_len, file_consts),
            FileKey.COMMENT_LINE_FLOW:                 comment_line(FileValue.COMMENT_LINE_FLOW, comment_line_len, file_consts),
            FileKey.COMMENT_LINE:                      comment_line('', comment_line_len, file_consts)
        })

    if tab_size and FileKey.TAB not in keys_vals and FileKey.TAB.value not in keys_vals:
        keys_vals[FileKey.TAB] = ' '*tab_size

    for k, v in keys_vals.items():
        v = v or ''

        if isinstance(k, Enum):
            k = k.value

        if isinstance(k, Enum):
            v = v.value

        s = s.replace(k, str(v))

    return s

def comment_line(
    text: Optional[Union[FileValue, str]],
    line_len: int,
    file_consts: FileConsts,
    tabs: Optional[int] = None,
    tab_size: Optional[int] = None
) -> str:
    import math

    filler_char = file_consts.comment_line_char
    filler_char = filler_char if len(filler_char) == 1 else filler_char[0]
    pre, post = '{} '.format(file_consts.comment_starter), ' {}'.format(file_consts.comment_ender)
    tabs = tabs or 0
    tab_size = tab_size or 0

    if isinstance(text, Enum):
        text = text.value

    text = ' {} '.format(text.strip()) if text else ''
    needeed_len = line_len - len(text) - len(pre) - len(post) - 2*tabs*tab_size
    pre_div_len = math.ceil(needeed_len/2)
    post_div_len = needeed_len - pre_div_len

    return '{} {}{}{} {}'.format(file_consts.comment_starter, pre_div_len*filler_char, text, post_div_len*filler_char, file_consts.comment_ender)


# -------------------------------------------------------------------------------------------------------------------------------- #