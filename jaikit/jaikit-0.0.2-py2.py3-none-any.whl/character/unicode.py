"""
Unicode字符集工具箱
用途：
查询某字符的Unicode所属区段及相关信息

示例：

    # >>> from jaikit.character.unicode import character_unicode_info
    # >>> character_unicode_info(character="我")

    {'平面': '0 BMP',
     '区段范围': 'U+4E00..U+9FFF',
     '区段名称': '中日韩统一表意文字',
     '英文名称': 'CJK Unified Ideographs',
     '码位数': '20,992',
     '已定义字元数': '20,989',
     '文字': '汉字',
     'start': 19968,
     'end': 40959}

参考资料：
维基百科页面2021年9月3日版本
https://zh.wikipedia.org/wiki/Unicode区段
https://liyucang-git.github.io/2019/06/17/彻底弄懂Unicode编码/
"""
import bisect

import pandas as pd

df = pd.read_pickle("jaikit/character/unicode_info.pkl")

breakpoints = df["start"]
section_indexes = list(range(-1, len(df["start"])))


def character_unicode_info(character: str):
    unicode_ord: int = ord(character)
    info = df.iloc[section_indexes[bisect.bisect(breakpoints, unicode_ord)]]
    if pd.isna(info["平面"]):
        raise ValueError("不是Unicode字符")
    else:
        info = info.append(pd.Series({"Unicode编码": unicode_ord}))
        return info
