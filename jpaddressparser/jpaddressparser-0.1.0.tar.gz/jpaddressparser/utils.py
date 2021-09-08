import csv
import re
from pathlib import Path

import jaconv

_target_regex = re.compile(r"(（.+）|以下に掲載がない場合)")


def read_japan_post_data(f: Path, encoding="sjis"):
    """Read Japan Post format address csv file

    Args:
        f (Path): path of the csv file
        encoding (str, optional): file encoding. Defaults to "sjis".

    Returns:
        Dict[str, Tuple[str, str, str]]: dictionary whose key is the concat of (prefecture,city,district) and the value is this tuple itself
    """
    with f.open("rt", encoding=encoding) as fp:
        reader = csv.reader(fp)
        # row[6]: prefecture, row[7]: city, row[8]: district
        rows = ((row[6], row[7], _target_regex.sub("", row[8])) for row in reader)
        return {r[0] + r[1] + r[2]: r for r in rows}


def normalize(address: str):
    """normalize kana, digits, ascii and spaces

    Args:
        address (str): address string

    Returns:
        str: normalized string
    """
    # halfwidth kana -> fullwidth kana
    s = jaconv.han2zen(address, kana=True, ascii=False, digit=False)
    # fullwitdh ascii and digits -> halfwidth
    s = jaconv.zen2han(s, kana=False, ascii=True, digit=True)
    # remove spaces
    s = s.replace(" ", "")
    return s
