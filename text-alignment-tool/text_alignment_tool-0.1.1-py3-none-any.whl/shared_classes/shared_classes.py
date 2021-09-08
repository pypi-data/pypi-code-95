from typing import NamedTuple
import numpy as np


LetterList = np.ndarray


class TextChunk(NamedTuple):
    start_idx: int
    end_idx: int
    name: str

