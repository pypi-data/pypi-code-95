from re import sub as _sub


def str_to_filename(text):
    return _sub(r'[^A-Za-z0-9.-]+', '_', text)


def parse_range(s: str):
    """Parse ranges such as 1,3,6-8,10 to 1,3,6,7,8,10"""
    return _sub(r'(\d+)-(\d+)', _replace_range_part, s)


def _replace_range_part(r):
    return ','.join(map(str, range(int(r[1]), int(r[2]))))
