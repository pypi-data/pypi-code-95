import string
import re


def remove_non_ascii_characters(text_input: str) -> str:
    """ Remove non-ascii characters from input text.
    
    :param text_input: Input text to be processed.
    :type text_input: `str`
    
    :return: Text without non-ASCII characters.
    :rtype: `str`
    """
    valid_characters = set(string.printable)
    accented_letters = {'á', 'é', 'í', 'ó', 'ú', 'à', 'â', 'ê', 'ô', 'ã', 'õ', 'ç'}
    valid_characters = valid_characters.union(accented_letters)
    
    return re.sub(' +', ' ', ''.join(filter(lambda x: x in valid_characters, text_input)))
