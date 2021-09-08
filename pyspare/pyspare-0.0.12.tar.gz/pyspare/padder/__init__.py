from .crostab_padder import crostab_padder
from .entries_padder import entries_padder
from .matrix_padder import matrix_padder
from .series_padder import series_padder
from .table_padder import table_padder
from .vector_padder import vector_padder


def pad_start(text: str, width: int, fill_char: str = ' '):
    return f'{text:{fill_char[0]}>{width}}'


def pad_end(text: str, width: int, fill_char: str = ' '):
    return f'{text:{fill_char[0]}<{width}}'


def pad_centered(text: str, width: int, fill_char: str = ' '):
    return f'{text:{fill_char[0]}^{width}}'
