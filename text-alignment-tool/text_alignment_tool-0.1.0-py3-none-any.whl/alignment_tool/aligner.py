from text_alignment_tool.src.shared_classes.shared_classes import LetterList, TextChunk
from text_alignment_tool.src.alignment_algorithms.alignment_algorithm import (
    TextAlignments,
)
from ..alignment_algorithms import AlignmentAlgorithm
from ..text_transformers import TextTransformer
from typing import NamedTuple, Union
from enum import Enum


class TextAlignmentException(Exception):
    pass


class AlignedIndices(NamedTuple):
    input_idx: int
    output_idx: int


class TextType(Enum):
    QUERY = 1
    TARGET = 2


class QueryTargetAlignment:
    def __init__(
        self,
        query_to_target_mapping: TextAlignments,
        query_text: LetterList,
        target_text: LetterList,
        query_text_chunks: list[TextChunk],
        target_text_chunks: list[TextChunk],
        query_transformer_class_name: str,
        target_transformer_class_name: str,
    ):
        self.query_to_target_mapping: TextAlignments = query_to_target_mapping
        self.query_text: LetterList = query_text
        self.target_text: LetterList = target_text
        self.query_text_chunks: list[TextChunk] = query_text_chunks
        self.target_text_chunks: list[TextChunk] = target_text_chunks
        self.__query_transformer_class_name = query_transformer_class_name
        self.__target_transformer_class_name = target_transformer_class_name
        self.__query_to_target_chunk_mapping: list[tuple[TextChunk, TextChunk]] = []

    @property
    def query_to_target_chunk_mapping(self) -> list[tuple[TextChunk, TextChunk]]:
        # TODO: perhaps update all such "cached properties" to @functools.cached_property
        # but support is touchy in python versions: @functools.cached_property >= Python 3.8;
        # @property + @functools.lru_cache() >= Python 3.2, < Python 3.8; ...
        if len(self.__query_to_target_chunk_mapping) > 0:
            return self.__query_to_target_chunk_mapping

        aligned_text_chunks_set: set[tuple[int, int]] = set([])
        aligned_text_chunks: list[tuple[TextChunk, TextChunk]] = []
        alignments_idx = 0
        while alignments_idx is not None and alignments_idx < len(
            self.query_to_target_mapping.alignments
        ):
            current_alignment = self.query_to_target_mapping.alignments[alignments_idx]
            stop_query = False
            for q_idx, query_text_chunk in enumerate(self.query_text_chunks):
                for t_idx, target_text_chunk in enumerate(self.target_text_chunks):
                    if (
                        query_text_chunk.start_idx
                        <= current_alignment.query_idx
                        <= query_text_chunk.end_idx
                        and target_text_chunk.start_idx
                        <= current_alignment.target_idx
                        <= target_text_chunk.end_idx
                    ):
                        if (q_idx, t_idx) not in aligned_text_chunks_set:
                            aligned_text_chunks_set.add((q_idx, t_idx))
                            aligned_text_chunks.append(
                                (query_text_chunk, target_text_chunk)
                            )
                        stop_query = True
                        break
                if stop_query:
                    break
            alignments_idx = alignments_idx + 1
        self.__query_to_target_chunk_mapping = aligned_text_chunks
        return self.__query_to_target_chunk_mapping

    @property
    def unaligned_query_text_chunks(self) -> list[TextChunk]:
        matched_query_chunks = [x[0] for x in self.query_to_target_chunk_mapping]
        return list(
            dict.fromkeys(
                [x for x in self.query_text_chunks if x not in matched_query_chunks]
            )
        )

    @property
    def unaligned_target_text_chunks(self) -> list[TextChunk]:
        matched_target_chunks = [x[1] for x in self.query_to_target_chunk_mapping]
        return list(
            dict.fromkeys(
                [x for x in self.target_text_chunks if x not in matched_target_chunks]
            )
        )

    @property
    def query_transformer_class_name(self):
        return self.__query_transformer_class_name

    @property
    def target_transformer_class_name(self):
        return self.__target_transformer_class_name


class AlignmentTextDataObject:
    def __init__(self):
        self.text: list[str] = []


class AlignmentOperation:
    """
    A container for the specific details of a transform or
    alignment operation.
    """

    def __init__(
        self,
        query_transformation: Union[TextTransformer, None],
        target_transformation: Union[TextTransformer, None],
        alignment: Union[AlignmentAlgorithm, None],
    ):
        self.query_transformation = query_transformation
        self.target_transformation = target_transformation
        self.alignment = alignment
