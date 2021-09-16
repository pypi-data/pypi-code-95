import typing as tp

from scanner.lexycal.lexycal_3 import Lexycal_3
from .token_type_dict import TOKEN_TYPES

LEX = Lexycal_3('PT_BR')


def get_tokens(text_input: str):
    """ Take Scanner call to tokenize the input text.

    :param text_input: Text to be tokenized.
    :type text_input: `str`
    :return: A tuple containing a list of the tokens and a list of the token types.
    :rtype: `tp.Tuple[tp.List[str]]`
    """
    LEX.get_tokens(input_text=text_input, no_heuristics=True)
    return LEX.tokens, LEX.output_token_types()


def drop_token_items(tokens_to_keep: tp.List[str]):
    """ Remove from token dictionary the data types that will not be tokenized.
    
    :param tokens_to_keep: Token types to be used.
    :type tokens_to_keep: `list` of `str`
    :return: Updated token dictionary.
    :rtype: `dict` of `TokenType` to `str`
    """
    tokens_copy = TOKEN_TYPES.copy()
    for key, item in TOKEN_TYPES.items():
        if item not in tokens_to_keep:
            del tokens_copy[key]
    return tokens_copy

