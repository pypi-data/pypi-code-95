import typing as tp

from scanner.lexycal.token_type import TokenType

from .take_scanner_caller import get_tokens
from .token_type_dict import TOKEN_TYPES


def tokenize_text(text_input: str, token_types: tp.Dict[TokenType, str] = TOKEN_TYPES):
    """ Replace CPFs, CNPJs, CEPs, Phones, Numbers and Codes with tokens.
    
    Possible data to be tokenized include: `DOC`, `CEP`, `PHONE`, `NUMBER`, `CODE`.
    
    :param text_input: Input to be tokenized.
    :type text_input: `str`
    :param token_types: Dictionary contained types to be tokenized. The default value considers all tokens.
    :type token_types: `dict`
    :return: Tokenized text.
    :rtype: `str`
    """
    tokens, tokens_type = get_tokens(text_input)
    tokenized_sentence = []
    
    for token, token_type in zip(tokens, tokens_type):
        if token_type in token_types.keys():
            tokenized_sentence.append(token_types[token_type])
        else:
            tokenized_sentence.append(token)
        
    return ' '.join(tokenized_sentence)[:-1]
