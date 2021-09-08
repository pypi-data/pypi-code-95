from text_alignment_tool.src.shared_classes import LetterList, TextChunk
from text_alignment_tool.src.text_transformers import TextTransformer
import numpy as np


class CharacterSubstitution:
    def __init__(self, input_character: str, output_character: str) -> None:
        self.input_character = self.verify_character(input_character)
        self.output_character = self.verify_character(output_character)

    @staticmethod
    def verify_character(char: str):
        if not isinstance(char, (str)):
            raise TypeError(f"Only str types are accepted: {char} is {type(char)} ")
        if len(char) != 1:
            raise Exception(
                f"Only single characters are accepted, but {char} with length {len(char)} was submitted."
            )
        return char


class SubstituteCharacterTransformer(TextTransformer):
    def __init__(self, substitution_list: list[CharacterSubstitution]):
        """Perform a transform of a single character to another single character

        Args:
            substitution_list (list[CharacterSubstitution]): a list of input/output character substitutions
        """
        self.substitution_list = substitution_list
        super().__init__()

    def load_input(self, input: LetterList, text_chunk_indices: list[TextChunk]):
        super().load_input(input, text_chunk_indices, False)

    def transform(self) -> LetterList:
        if np.any(self._output):
            return self._output

        self.__transform()

        return super().transform()

    def __transform(self):
        replacement_codes = {
            ord(x.input_character): ord(x.output_character)
            for x in self.substitution_list
        }

        self._input_output_map = [(idx, idx) for idx in range(len(self.input))]
        self._output = np.vectorize(replacement_codes.get)(self.input, self.input)
        self._text_chunk_indices = self._input_text_chunk_indices
