from jaikit.character.unicode import WIKI_UNICODE_INFO
from itertools import chain


# 包含汉字的区段
CHN_PART = WIKI_UNICODE_INFO.loc[WIKI_UNICODE_INFO["文字"].str.contains("汉字", na=False)]
CHINESE_ORDS = {
    _
    for _ in chain(
        *(range(item["start"], item["end"] + 1) for idx, item in CHN_PART.iterrows())
    )
}
REMOVE_CHINESE_MAP = {_: "" for _ in CHINESE_ORDS}


def contains_chinese(text: str) -> bool:
    """基于Unicode字符集的汉字所涉及范围，判断一个字符串是否含有汉字"""
    return any((ord(character) in CHINESE_ORDS for character in text))


def remove_chinese(text: str) -> str:
    """基于Unicode码表汉字区段，从字符串中删除所有汉字"""
    return text.translate(REMOVE_CHINESE_MAP)
