from .lower_case import to_lower_case
from .replace_abbreviations import replace_abbreviations
from .abbreviations import ABBREVIATIONS


def base_preprocessing(text_input: str) -> str:
    """Apply basic preprocessing methods on text.

    :param text_input: Input to be processed.
    :type text_input: `str`
    :return: Processed text
    :rtype: `str`
    """
    sentence = to_lower_case(text_input)
    sentence = replace_abbreviations(sentence, ABBREVIATIONS)
    return sentence
