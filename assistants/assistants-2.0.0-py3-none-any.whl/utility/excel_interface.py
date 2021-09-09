from __future__ import annotations

from typing import TYPE_CHECKING

import openpyxl
from pandas.io.excel._openpyxl import OpenpyxlWriter  # NoQA
import pandas.io.formats.excel

if TYPE_CHECKING:
    from pathlib import Path

    import pandas as pd

# Override pandas excel styles
pandas.io.formats.excel.ExcelFormatter.header_style = None  # NoQA


def load_workbook(filename: Path) -> pd.ExcelWriter:
    """Loads a workbook in a way that enables within-sheet overwriting.

    See https://github.com/pandas-dev/pandas/issues/42221, https://github.com/pandas-dev/pandas/pull/42222

    """
    # try to open an existing workbook
    book = openpyxl.load_workbook(filename)
    # create writer
    writer = OpenpyxlWriter(filename)
    writer.datetime_format = "DD/MM/YYYY"  # not passed to super() by OpenpyxlWriter, override here
    # patch in loaded workbook, copy existing sheets
    writer.book = book
    writer.sheets = {ws.title: ws for ws in book.worksheets}

    return writer
