api = '''
[COMMENT_LINE_IMPORTS]

# System
from typing import Optional, Dict

# Pip
from ksimpleapi import Api

# Local


[COMMENT_LINE]



[TAB][COMMENT_LINE_CLASS_NAME]

class [CLASS_NAME](Api):

[COMMENT_LINE_OVERRIDES]

[TAB]@classmethod
[TAB]def extra_headers(cls) -> Optional[Dict[str, any]]:
[TAB][TAB]return {

[TAB][TAB]}


[TAB][COMMENT_LINE_PUBLIC_PROPERTIES]




[TAB][COMMENT_LINE_PUBLIC_METHODS]




[TAB][COMMENT_LINE_PRIVATE_PROPERTIES]




[TAB][COMMENT_LINE_PRIVATE_METHODS]




[COMMENT_LINE]
'''.strip()