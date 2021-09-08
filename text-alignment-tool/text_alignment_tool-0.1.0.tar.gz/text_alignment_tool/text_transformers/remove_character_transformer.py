from text_alignment_tool.src.shared_classes import LetterList, TextChunk
from text_alignment_tool.src.text_transformers import TextTransformer
import numpy as np


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


class RemoveCharacterTransformer(TextTransformer):
    def __init__(self, remove_character_list: list[RemoveCharacter]):
        """Remove every instance of the submitted characters

        Args:
            substitution_list (list[CharacterSubstitution]): a list of characters to be removed
        """
        self.__remove_character_list = remove_character_list
        super().__init__()

    def load_input(self, input: LetterList, text_chunk_indices: list[TextChunk]):
        super().load_input(input, text_chunk_indices, False)

    def transform(self) -> LetterList:
        if np.any(self._output):
            return self._output

        self.__transform()

        return super().transform()

    def __transform(self):
        remove_characters = set(
            [ord(x.remove_character) for x in self.__remove_character_list]
        )

        output: list[int] = []
        output_chunks: list[TextChunk] = []
        input_output_map: list[tuple[int, int]] = []
        for chunk in self._input_text_chunk_indices:
            output_chunk_start_idx = len(output)
            chunk_text = self.input[chunk.start_idx : chunk.end_idx + 1]
            for idx, token in enumerate(chunk_text):
                if token in remove_characters:
                    continue  # Just don't add the token to output to "remove" it
                current_idx = chunk.start_idx + idx
                output.append(token)
                input_output_map.append((current_idx, len(output) - 1))

            if output_chunk_start_idx <= len(output) - 1:
                output_chunks.append(
                    TextChunk(output_chunk_start_idx, len(output) - 1, chunk.name)
                )

        self._input_output_map = input_output_map
        self._output = np.array(output, dtype=np.uint32)
        self._text_chunk_indices = output_chunks
