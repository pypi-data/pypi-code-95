from text_alignment_tool.src.shared_classes import LetterList, TextChunk
from text_alignment_tool.src.text_transformers import TextTransformer
from itertools import zip_longest
import numpy as np


class MultipleCharacterSubstitution:
    def __init__(self, input_characters: str, output_characters: str) -> None:
        if input_characters == output_characters:
            raise Exception(
                "Input and output strings are the same, no passthroughs allowed."
            )
        if len(input_characters) == 0:
            raise Exception("Input characters is empty.")
        self.input_characters = np.array(
            [ord(x) for x in self.verify_characters(input_characters)]
        )
        self.output_characters = np.array(
            [ord(x) for x in self.verify_characters(output_characters)]
        )

    @staticmethod
    def verify_characters(char: str):
        if not isinstance(char, (str)):
            raise TypeError(f"Only str types are accepted: {char} is {type(char)} ")
        return char


class SubstituteMultipleCharactersTransformer(TextTransformer):
    def __init__(self, substitutions_list: list[MultipleCharacterSubstitution]):
        """Perform a transform of a single character to another single character

        Args:
            substitution_list (list[CharacterSubstitution]): a list of input/output character substitutions
        """
        self.substitutions_list = substitutions_list
        super().__init__()

    # def load_input(self, input: LetterList, text_chunk_indices: list[TextChunk]):
    #     super().load_input(input, text_chunk_indices, False)

    def transform(self) -> LetterList:
        if np.any(self._output):
            return self._output

        self.__transform()

        return super().transform()

    def __transform(self):
        replacement_transforms = [x.input_characters for x in self.substitutions_list]
        output = np.array([], dtype=np.uint32)
        input_output_map: list[tuple[int, int]] = []
        output_chunks: list[TextChunk] = []
        for chunk in self._input_text_chunk_indices:
            output_chunk_start_idx = len(output)
            chunk_text = self.input[chunk.start_idx : chunk.end_idx + 1]
            altered_chunk_text = chunk_text.copy()
            chunk_in_out_map = [(x, x) for x in range(chunk_text.size)]
            matches_found = True
            while matches_found:
                matches_found = False
                for idx, search_text in enumerate(replacement_transforms):
                    matches = find_sequence_in_array(search_text, altered_chunk_text)
                    if not matches:
                        continue
                    matches_found = True
                    replacement_text = self.substitutions_list[idx].output_characters
                    replacement_offset = replacement_text.size - search_text.size
                    altered_text_offset = chunk_text.size - altered_chunk_text.size
                    altered_chunk_text = np.concatenate(
                        (
                            altered_chunk_text[: matches[0][0]],
                            replacement_text,
                            altered_chunk_text[matches[0][0] + search_text.size :],
                        )
                    ).astype(np.uint32)
                    max_middle_altered_chunk = (matches[0][0] + search_text.size) % (
                        matches[0][0] + replacement_text.size
                    )
                    new_starting_chunk_map = chunk_in_out_map[0 : matches[0][0]]
                    new_middle_chunk_map = [
                        (i + altered_text_offset, o)
                        for o, i in zip_longest(
                            range(
                                matches[0][0],
                                matches[0][0] + replacement_text.size,
                            ),
                            range(matches[0][0], max_middle_altered_chunk),
                            fillvalue=max_middle_altered_chunk - 1,
                        )
                    ]
                    new_ending_chunk_map = [
                        (x[0], x[1] + replacement_offset)
                        for x in chunk_in_out_map[matches[0][0] + search_text.size :]
                    ]
                    chunk_in_out_map = (
                        new_starting_chunk_map
                        + new_middle_chunk_map
                        + new_ending_chunk_map
                    )

            output = np.concatenate((output, altered_chunk_text))
            input_output_map = input_output_map + [
                (chunk.start_idx + x[0], output_chunk_start_idx + x[1])
                for x in chunk_in_out_map
            ]
            if output_chunk_start_idx <= len(output) - 1:
                output_chunks.append(
                    TextChunk(output_chunk_start_idx, len(output) - 1, chunk.name)
                )

        self._input_output_map = input_output_map
        self._output = output
        self._text_chunk_indices = output_chunks


def find_sequence_in_array(seq: np.ndarray, arr: np.ndarray) -> list[int]:
    """Find sequence in an array using NumPy only.
        See: https://stackoverflow.com/questions/36522220/searching-a-sequence-in-a-numpy-array

    Parameters
    ----------
    arr    : input 1D array
    seq    : input 1D array

    Output
    ------
    Output : 1D list of starting indices in the input array that satisfy the
    matching of input sequence in the input array.
    In case of no match, an empty list is returned.
    """

    # Store sizes of input array and sequence
    Na, Nseq = arr.size, seq.size
    if Na == 0 or Nseq == 0:
        return []

    # Range of sequence
    r_seq = np.arange(Nseq)

    # Create a 2D array of sliding indices across the entire length of input array.
    # Match up with the input sequence & get the matching starting indices.
    M = (arr[np.arange(Na - Nseq + 1)[:, None] + r_seq] == seq).all(1)

    # Get the range of those indices as final output
    if M.any() > 0:
        return np.where(M)
    else:
        return []
