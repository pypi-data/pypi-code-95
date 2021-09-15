NBSP = '\u00A0'
NNBSP = '\u202F'
WHSP = ' '
ANYSP = fr'[{WHSP}{NBSP}{NNBSP}]'

NDASH = '–'
MDASH = '—'
MDASH_PAIR = NBSP + MDASH + WHSP

MINUS = '−'
TIMES = '×'

LSQUO = '‘'  # left curly quote mark
RSQUO = '’'  # right curly quote mark/apostrophe
LDQUO = '“'  # left curly quote marks
RDQUO = '”'  # right curly quote marks
DLQUO = '„'  # double low curly quote mark
LAQUO = '«'  # left angle quote marks
RAQUO = '»'  # right angle quote marks

SPRIME = '′'
DPRIME = '″'
