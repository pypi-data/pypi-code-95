import sys

v1, v2, *_ = sys.version.split('.')
version = int(v1) + int(v2) / 10
if version < 3.6:
    raise RuntimeError('python 版本要求大于3.6')

hard_dependencies = ("pandas", "pathlib", "openpyxl", "multiprocessing")
missing_dependencies = []

for dependency in hard_dependencies:
    try:
        __import__(dependency)
    except ImportError as e:
        missing_dependencies.append(f"{dependency}: {e}")

if missing_dependencies:
    raise ImportError(
        "Unable to import required dependencies:\n" + "\n".join(missing_dependencies)
    )
del hard_dependencies, dependency, missing_dependencies

EXCEL_TYPE = '.xls'
__version__ = '1.0.3'

from .fileunion import (union_in_path_to_csv, union_in_list_to_csv, union_in_path_to_sheets, union_in_list_to_sheets)
from .filesplit import (split_by_row, split_by_size, split_by_column, mml_split_file)
from .filereader import FileReader
