from itertools import groupby
from typing import Counter, Union
import numpy as np
import re
import bidict


# See https://stackoverflow.com/questions/4998629/split-string-with-multiple-delimiters-in-python
def split(delimiters: list[str], string: str, maxsplit: int = 0) -> list[str]:
    regexPattern = "|".join(map(re.escape, delimiters))
    return re.split(regexPattern, string, maxsplit)


def letter_list_to_unique_word_codes(
    letter_list: np.ndarray, separators: Union[list[str], None] = None
) -> tuple[np.ndarray, bidict.bidict[str, int], dict[int, list[int]]]:
    """
    This assigns a unique number to each unique word in the submitted
    text. It returns an array with the text represented by its unique
    word codes along with the word_code_key.
    """

    if separators is None:
        separators = [" "]

    indexed_text = [(chr(x), idx) for idx, x in enumerate(letter_list)]
    word_chunks = (
        list(g)
        for k, g in groupby(indexed_text, key=lambda x: x[0] not in separators)
        if k
    )
    word_map: dict[str, int] = {}
    coded_output: list[int] = []
    word_to_letter_map: dict[int, list[int]] = {}
    current_word_idx = 0
    for idx, word in enumerate(word_chunks):
        text_word = "".join([x[0] for x in word])
        if text_word not in word_map:
            word_map[text_word] = current_word_idx
            current_word_idx = current_word_idx + 1
        coded_output.append(word_map[text_word])
        word_to_letter_map[idx] = [x[1] for x in word]

    return (
        np.array(coded_output).astype(np.uint32),
        bidict.bidict(word_map),
        word_to_letter_map,
    )


def find_wordlist_for_alignment(
    input_gold_text: np.ndarray, max_word_frequency: int = 100
) -> list[int]:
    gold_text_map = [
        x[0] for x in Counter(input_gold_text).items() if x[1] < max_word_frequency
    ]
    return list(set(gold_text_map))


def filter_wordlist(
    wordlist: np.ndarray, valid_values: list[int]
) -> tuple[np.ndarray, dict[int, int]]:
    filtered_list = [(idx, x) for idx, x in enumerate(wordlist) if x in valid_values]
    return np.array([x[1] for x in filtered_list]).astype(np.uint32), {
        x[0]: idx for idx, x in enumerate(filtered_list)
    }
