import logging
import swalign
from .alignment_algorithm import AlignmentAlgorithm, TextAlignments, AlignmentKey
from ..shared_classes import TextChunk


class LocalAlignmentAlgorithm(AlignmentAlgorithm):
    def __init__(self):
        super().__init__()

    def align(self) -> TextAlignments:
        """
        Perform a local alignment of the query and target.  Primarily
        this is useful for finding a small chunk of query text within
        a large chunk of target text. It will probably not be able to
        provide a good  alignment on the letter level, but it should be
        quite close on the chunk level. The output of
        `output_query_text_chunk_indices` and
        `output_target_text_chunk_indices` can be used to find a more
        precise global alignment.
        """

        if len(self._input_query_text_chunk_indices) != len(
            self._input_target_text_chunk_indices
        ):
            logging.warning(
                f"Since the query has {len(self._input_query_text_chunk_indices)} text chunks and the target has {len(self._input_target_text_chunk_indices)}, the alignment will probably not work as intended."
            )

        output_query_chunks: list[TextChunk] = []
        output_target_chunks: list[TextChunk] = []
        query_start_end = [
            (x.start_idx, x.end_idx) for x in self._input_query_text_chunk_indices
        ]
        target_start_end = [
            (x.start_idx, x.end_idx) for x in self._input_target_text_chunk_indices
        ]
        for (query_start_idx, query_end_idx), (target_start_idx, target_end_idx) in zip(
            query_start_end, target_start_end
        ):
            alignments = local_alignment(
                self._query[query_start_idx : query_end_idx + 1],
                self._target[target_start_idx : target_end_idx + 1],
            )
            output_query_chunks.append(TextChunk(alignments[0], alignments[1]))
            output_target_chunks.append(TextChunk(alignments[2], alignments[3]))

        # Note that these alignments will probably not be very good
        text_alignments: list[AlignmentKey] = []
        for query_chunk, target_chunk in zip(output_query_chunks, output_target_chunks):
            max_target_idx = target_chunk.end_idx + 1
            for idx in range(query_chunk.end_idx - query_chunk.start_idx + 1):
                query_idx = query_chunk.start_idx + idx
                target_idx = (
                    target_chunk.start_idx + idx
                    if target_chunk.start_idx + idx < max_target_idx
                    else max_target_idx
                )
                text_alignments.append(AlignmentKey(query_idx, target_idx))

        # Save alignments to self object
        self._output_query_text_chunk_indices = output_query_chunks
        self._output_target_text_chunk_indices = output_target_chunks
        self._alignment.alignments = text_alignments

        return super().align()


def local_alignment(query_text, target_text) -> tuple[int, int, int, int]:
    # choose your own values here… 2 and -1 are common.
    match = 2
    mismatch = -1
    scoring = swalign.NucleotideScoringMatrix(match, mismatch)

    sw = swalign.LocalAlignment(scoring)  # you can also choose gap penalties, etc...
    target_transcription = " ".join([chr(x) for x in target_text])
    query_transcription = " ".join([chr(x) for x in query_text])
    alignment = sw.align(target_transcription, query_transcription)
    start_idx, end_idx, query_start, query_end = (
        alignment.r_pos,
        alignment.r_end,
        alignment.q_pos,
        alignment.q_end,
    )
    alignment.dump()
    return start_idx, end_idx, query_start, query_end
