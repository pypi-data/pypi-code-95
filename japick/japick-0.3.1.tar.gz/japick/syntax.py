import re

NULL_SYMBOL = "~"
MASK_SYMBOL = "_"

JA_REGEX = re.compile(
    "["
    "\u3041-\u309F"  # HIRAGANA
    "\u30A1-\u30FF"  # KATAKANA
    "\u2E80-\u2FDF\u3005-\u3007\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF"  # KANJI
    "\U00020000-\U0002EBEF"  # KANJI
    "]+"
)

HEAD_REGEX = re.compile("^#+")
LIST_REGEX = re.compile(r"^\s*([*-]|\d+\.) (\[[x ]?] )?")
QUOTE_REGEX = re.compile(r"^>+\s*")
HTML_REGEX = re.compile(r"<.+?>")

URL_REGEX = re.compile(r"<?(http|https|ftp)://[-a-zA-Z0-9@:%_+.~#?&/=]+>?")
LINK_REGEX = re.compile(r"(!?\[)(.*?)(]\(.*?\))")
CODE_REGEX = re.compile(r"`.+?`")
SYMBOL_REGEX = re.compile(r"(\*|___|__|~)")  # ASCII Symbols to clean

FENCE_START = re.compile("^```.+$")
FENCE_END = re.compile("^```$")
