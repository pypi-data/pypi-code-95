import logging
from abc import ABC, abstractmethod
from io import StringIO
from pprint import pformat as pp
from typing import Iterable, List, Tuple, Union

import numpy as np


def version_ge(v1: str, v2: str) -> bool:
    """
    Check a version against another.

    return True if `v1` > `v2` (`v1` more recent than `v2`),
    or if `v2` is 0 or None.

    This function is very naive for now, just comparing v1 and v2 as float.

    Maybe use semver instead (https://pypi.org/project/semver/)?

    >>> version_ge("8.2", "9.1")
    False
    >>> version_ge("8.3", "")
    True
    """
    if not v2:
        return True
    return float(v1) >= float(v2)


def read_array(
    content: List[str], line_no: int, fields: List[str], coerce: List[type]
) -> np.ndarray:
    """
    extract and turn a bunch of lines into a numpy structured array (by default).

    >>> txt = '''line 1,
    ... line 2,
    ... line 3, bla, bla,
    ... 1, 10,
    ... 2, 20,
    ... 3, 30,
    ... 4, -5
    ... -1, 0
    ... bla, bla,
    ... '''
    >>> txt = txt.split('\\n')
    >>> data = read_array(txt, line_no=3, fields=('col1', 'col2'), coerce=(int, float))
    >>> data
    array([(1, 10.), (2, 20.), (3, 30.), (4, -5.)],
          dtype=[('col1', '<i8'), ('col2', '<f8')])

    which can be easily turned to pandas df:

    >>> import pandas as pd
    >>> df = pd.DataFrame(data)
    >>> print(df)
       col1  col2
    0     1  10.0
    1     2  20.0
    2     3  30.0
    3     4  -5.0

    """
    read_lines = 0
    data = []
    for line in content[line_no:]:
        if line.strip().startswith("-1"):
            break
        data.append(tuple(line.strip().strip(",").split(",")))
    return np.array(data, dtype=list(zip(fields, coerce)))


# =============================================================================
# blocks
# =============================================================================
class Block(ABC):
    """
    Abstract Base Class for Neutral blocks.

    Mandatory methods to ovverride are:
        * `digest`: a classmethod converting a list of structured parsed data
        into the expected end-user data structure.
    """

    RECORDS = []  # to be overwritten by children

    def __init__(self, version: str):
        # clean specs and remove fields when current version doesn't match
        for rno, records in enumerate(self.RECORDS):
            records = [r for r in records if version_ge(version, r.get("v+"))]
            self.RECORDS[rno] = records
        # clen empty mist
        self.RECORDS = [s for s in self.RECORDS if s]
        # from pprint import pprint as pp
        # pp(self.RECORDS)
        self.data = []
        self.flavor = None

    @classmethod
    def id(cls):
        return int(cls.__name__[1:])

    def parse(self, content: Union[StringIO, str, Iterable[str]]) -> None:
        """parse provided `content`.
        `content`may be either:
            * a file-like object
            * a single multi-line string
            * an iterable (list or tuple) of strings
        """
        if isinstance(content, StringIO):
            content = [l.rstrip("\n") for l in content.readlines()]
        elif isinstance(content, str):
            content = content.split("\n")
        else:
            content = [l.rstrip("\n") for l in content]
        content = [e for e in content if e]  # drop empty strings

        next_lines_to_read = 1
        lines_offset = 0  # in case some loose lines exist like eg. block450 "notes"
        # ---------------------------------------------------------------------
        # one block [-1 ... -1] can be made of several blocks
        # without the -1 / -1 signal!
        _content_loop = 0  # debugging-only purposes
        while content:
            data = {}
            for fields_set_no, fields_set in enumerate(self.RECORDS):
                # -----------------------------------------------------------------
                # for each set of fields (list of dictionnaries)
                line_no = lines_offset + fields_set_no
                lines = "\n".join(
                    content[line_no : line_no + next_lines_to_read]
                ).replace("<NULL>", "")
                lines_offset += next_lines_to_read - 1
                # -----------------------------------------------------------------
                # if single-line multi-fields, split fields by coma
                # this may be reveresed for `comp` fields later on
                if next_lines_to_read == 1:
                    fields = [f.strip() for f in lines.strip(",").split(",")]
                # -----------------------------------------------------------------
                # if multi-line, single-field, just wrap the lines into a list
                else:
                    fields = [lines]
                for field_no, field_specs in enumerate(fields_set):
                    fieldname = field_specs.get("field")
                    coerce_func = field_specs.get("coerce", lambda x: x)
                    # -------------------------------------------------------------
                    # read multi-line array
                    if field_specs.get("multi_line_array", False):
                        field_specs.get("multi_line_array")
                        records = read_array(
                            content,
                            line_no,
                            field_specs["fields"],
                            field_specs["coerce"],
                        )
                        lines_offset += len(records)
                    # -------------------------------------------------------------
                    # read single-line array
                    elif field_specs.get("single_line_array", False):
                        # one field wraps an array
                        nbi = field_specs["single_line_array"]
                        records = [coerce_func(e) for e in fields[:nbi]]
                    # -------------------------------------------------------------
                    # single-line, single-field
                    elif field_specs.get("one_field", False):
                        # rejoin previously splitted line
                        records = ", ".join(fields)
                    # -------------------------------------------------------------
                    # single-line, multi-fields
                    else:
                        try:
                            field = coerce_func(fields[field_no])
                        except Exception as exc:
                            logging.critical(
                                f"loop#{_content_loop}:: cannot coerce field#{field_no} {fields[field_no]=} with {coerce_func}"
                            )
                            logging.critical(f"{lines_offset=}")
                            logging.critical(f"{fields_set_no=}")
                            logging.critical(pp(content))
                            raise
                        # if current field describe nb of next lines to read:
                        if field_specs.get("is_offset", False):
                            next_lines_to_read = field
                            continue
                        else:
                            next_lines_to_read = 1
                            records = field
                    data[fieldname] = records
            else:
                # last_line = lines_offset + fields_set_no
                # _parsed_content = content[:last_line]
                # if self.__class__.__name__ == "B451":
                #     breakpoint()
                content = content[lines_offset + fields_set_no + 1 :]
                lines_offset = 0
                # remove dummy data:
                if "_" in data:
                    del data["_"]
                self.data.append(data)
                _content_loop += 1
            # return data

    @abstractmethod
    def digest(self):
        pass

    def _clean_default(self, txt):
        return txt.strip().strip(",").strip()


if __name__ == "__main__":
    import doctest

    doctest.testmod(optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
