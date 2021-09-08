from pathlib import Path
from typing import Any, NamedTuple
import numpy as np
from ..shared_classes import TextChunk, LetterList


class LoaderError(Exception):
    pass


# TODO: the loader should probably be able to recreate the original
# query text, but replacing its text with the aligned target text.
class TextLoader:
    """
    Instructions for converting the input source into
    the data structures used by the alignment tool.
    """

    def __init__(self, file_path: Path):
        self._file_path = file_path
        self._output: np.ndarray = np.array([], dtype=np.uint32)
        self._input_output_map: Any = None
        self._text_chunk_indices: list[TextChunk] = []

    def _load(self) -> LetterList:
        if self._output.size > 0:
            return self._output

        raise LoaderError("Transform action resulted in empty output")

    @property
    def output(self) -> LetterList:
        if self._output.size == 0:
            _ = self._load()

        if self._output.size > 0:
            return self._output

        raise LoaderError("Output is empty")

    @property
    def input_output_map(self) -> Any:
        if not self._input_output_map:
            _ = self.output

        if self._input_output_map:
            return self._input_output_map

        raise LoaderError("Input output map is empty")

    @property
    def text_chunk_indices(self) -> list[TextChunk]:
        if not self._text_chunk_indices:
            self._text_chunk_indices.append(TextChunk(0, self.output.size, ""))

        if self._text_chunk_indices:
            return self._text_chunk_indices

        raise LoaderError("No text chunk was created (this is a development error)")
