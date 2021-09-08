from text_alignment_tool.src.shared_classes import LetterList, TextChunk
from text_alignment_tool.src.text_transformers import TextTransformer
import numpy as np


class BracketingPair:
    def __init__(self, first_token: str, second_token: str) -> None:
        self.__pair = [
            self.verify_character(first_token),
            self.verify_character(second_token),
        ]
        self.__original_order = [ord(first_token), ord(second_token)]

    @staticmethod
    def verify_character(char: str):
        if not isinstance(char, (str)):
            raise TypeError(f"Only str types are accepted: {char} is {type(char)} ")
        if len(char) != 1:
            raise Exception(
                f"Only single characters are accepted, but {char} with length {len(char)} was submitted."
            )
        return ord(char)

    def __getitem__(self, i: int):
        return self.__pair[i]

    def __len__(self):
        return len(self.__pair)

    def __eq__(self, other: int):
        return other in self.__pair

    def reverse(self):
        self.__pair.reverse()

    def reset(self):
        self.__pair[0] = self.__original_order[0]
        self.__pair[1] = self.__original_order[1]


class RemoveCharacter:
    def __init__(self, remove_character: str) -> None:
        self.remove_character = self.verify_character(remove_character)

    @staticmethod
    def verify_character(char: str):
        if not isinstance(char, (str)):
            raise TypeError(f"Only str types are accepted: {char} is {type(char)} ")
        if len(char) != 1:
            raise Exception(
                f"Only single characters are accepted, but {char} with length {len(char)} was submitted."
            )
        return char


class ConsistentBracketingTransformer(TextTransformer):
    def __init__(self, bracketing_pair_list: list[BracketingPair]):
        """Look for pairs of bracketing characters and ensure they are
        paired consistently.

        Args:
            substitution_list (list[CharacterSubstitution]): a list of characters to be removed
        """
        self.__bracketing_pair_list = bracketing_pair_list
        super().__init__()

    def load_input(self, input: LetterList, text_chunk_indices: list[TextChunk]):
        super().load_input(input, text_chunk_indices, False)

    def transform(self) -> LetterList:
        if np.any(self._output):
            return self._output

        self.__transform()

        return super().transform()

    def __transform(self):
        output: list[int] = []
        for chunk in self._input_text_chunk_indices:
            chunk_text = self.input[chunk.start_idx : chunk.end_idx + 1]
            for token in chunk_text:
                for bracketing_pair in self.__bracketing_pair_list:
                    if token in bracketing_pair:
                        if token != bracketing_pair[0]:
                            token = bracketing_pair[0]
                        bracketing_pair.reverse()
                output.append(token)
            for bracketing_pair in self.__bracketing_pair_list:
                bracketing_pair.reset()

        self._output = np.array(output, dtype=np.uint32)
        self._input_output_map = [(idx, idx) for idx in range(self._output.size)]
        self._text_chunk_indices = self._input_text_chunk_indices
