import typing as tp

from .tokenize_text_input import tokenize_text
from .take_scanner_caller import drop_token_items


def tokenizer_preprocessing(text_input: str, processing_parameters: tp.List[str]):
    """Apply tokenizer preprocessing methods on text.

    :param text_input: Input to be processed.
    :type text_input: `str`
    :param processing_parameters: Processing types to be applied. Current types supported are 'doc', 'code',
         'phone', 'cep' and 'num'.
    :type processing_parameters: `tp.List[str]`
    :return: Processed text
    :rtype: `str`
    """
    parameter_dictionary = drop_token_items(processing_parameters)
    
    return tokenize_text(text_input, parameter_dictionary)

