import logging
import edlib
from .alignment_algorithm import AlignmentAlgorithm, TextAlignments, AlignmentKey
from ..shared_classes import LetterList, TextChunk


class GlobalAlignmentAlgorithm(AlignmentAlgorithm):
    def __init__(self):
        super().__init__()

    def align(self) -> TextAlignments:
        if self._alignment.alignments:
            return self._alignment

        self._alignment = global_alignment(self._query, self._target, self._input_query_text_chunk_indices, self._input_target_text_chunk_indices)
        return self._alignment


def global_alignment(query_text: LetterList, target_text: LetterList, query_text_chunks: list[TextChunk], target_text_chunks: list[TextChunk]) -> TextAlignments:
    alignments = TextAlignments()

    if len(query_text_chunks) != len(target_text_chunks):
        logging.warning(f'Since the query has {len(query_text_chunks)} text chunks and the target has {len(target_text_chunks)}, the alignment will probably not work as intended.')

    query_start_end = [(x.start_idx, x.end_idx) for x in query_text_chunks]
    target_start_end = [(x.start_idx, x.end_idx) for x in target_text_chunks]
    for (query_start_idx, query_end_idx), (target_start_idx, target_end_idx) in zip(query_start_end, target_start_end):
    # for query_text_chunk, target_text_chunk in zip(chunked_query_text, chunked_target_text):
        query_text_chunk = query_text[query_start_idx:query_end_idx]
        target_text_chunk = target_text[target_start_idx:target_end_idx]
        query = ''.join([chr(x) for x in query_text_chunk])
        target = ''.join([chr(x) for x in target_text_chunk])

        result = edlib.align(query, target, task = "path", mode='HW')
        nice = edlib.getNiceAlignment(result, query, target)
        query_count_idx = query_start_idx
        target_count_idx = target_start_idx
        for idx in range(len(nice['query_aligned'])):
            alignments.alignments.append(AlignmentKey(query_count_idx,target_count_idx))
            if nice['query_aligned'][idx] != '-':
                query_count_idx += 1
            if nice['target_aligned'][idx] != '-':
                target_count_idx += 1        

    return alignments
