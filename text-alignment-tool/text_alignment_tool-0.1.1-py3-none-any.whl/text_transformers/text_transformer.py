from ..alignment_algorithms import TextAlignments, AlignmentKey
from ..shared_classes import LetterList, TextChunk
import numpy as np


class TransformerError(Exception):
    pass


class TextTransformer:
    """
    Instructions for a specific text transformation operation.
    """

    def __init__(self):
        self._input: LetterList = np.array([], dtype=np.uint32)
        self._output: LetterList = np.array([], dtype=np.uint32)
        self._input_output_map: list[tuple[int, int]] = []
        self._input_text_chunk_indices: list[TextChunk] = []
        self._text_chunk_indices: list[TextChunk] = []

    def load_input(
        self,
        input: LetterList,
        text_chunk_indices: list[TextChunk],
        no_transform: bool = False,
    ):
        if self._input.size > 0:
            return

        self._input = input.astype(np.uint32)
        self._input_text_chunk_indices = text_chunk_indices

        if no_transform:
            self._output = self._input
            self._input_output_map = [(idx, idx) for idx in range(len(self._input))]
            self._text_chunk_indices = self._input_text_chunk_indices

        self.transform()

    def transform(self) -> LetterList:
        if self._output.size > 0:
            return self._output

        raise TransformerError("Transform action resulted in empty output")

    def apply_alignment(self, alignment_pairs: TextAlignments) -> TextAlignments:
        # Note: I think this will only work when the input length is >= the output length
        input_to_aligned_text_map = TextAlignments()
        alignment_pairs_dict: dict[int, list[int]] = {}

        for alignment in alignment_pairs.alignments:
            if alignment.query_idx not in alignment_pairs_dict:
                alignment_pairs_dict[alignment.query_idx] = []

            alignment_pairs_dict[alignment.query_idx].append(alignment.target_idx)

        for input_idx, output_idx in self.input_output_map:
            if output_idx in alignment_pairs_dict:
                for align_idx in alignment_pairs_dict[output_idx]:
                    input_to_aligned_text_map.alignments.append(
                        AlignmentKey(input_idx, align_idx)
                    )

        return input_to_aligned_text_map

    @property
    def input(self) -> LetterList:
        if np.any(self._input):
            return self._input

        raise TransformerError("Input is empty")

    @property
    def output(self) -> LetterList:
        if not np.any(self._output):
            _ = self.transform()

        if np.any(self._output.size):
            return self._output

        raise TransformerError("Output is empty")

    @property
    def input_output_map(self) -> list[tuple[int, int]]:
        if not self._input_output_map:
            _ = self.output

        if self._input_output_map:
            return self._input_output_map

        raise TransformerError("Input output map is empty")

    @property
    def input_text_chunk_indices(self) -> list[TextChunk]:
        return self._input_text_chunk_indices

    @property
    def text_chunk_indices(self) -> list[TextChunk]:
        if not self._text_chunk_indices:
            self._text_chunk_indices.append(TextChunk(0, self.output.size))

        if self._text_chunk_indices:
            return self._text_chunk_indices

        raise TransformerError(
            "No text chunk was created (this is a development error)"
        )
