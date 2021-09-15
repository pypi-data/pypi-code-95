from .lower_case import to_lower_case
from .remove_non_ascii import remove_non_ascii_characters


def base_preprocessing(text_input: str):
    """Apply basic preprocessing methods on text.

    :param text_input: Input to be processed.
    :type text_input: `str`
    :return: Processed text
    :rtype: `str`
    """
    sentence = to_lower_case(text_input)
    return remove_non_ascii_characters(sentence)
