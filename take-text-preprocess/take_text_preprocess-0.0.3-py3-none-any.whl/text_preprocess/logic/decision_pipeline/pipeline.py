import typing as tp

from text_preprocess.logic.basic_preprocessing.basic_callable import base_preprocessing
from text_preprocess.logic.add_space_to_puct import add_space_to_punctuation
from text_preprocess.logic.regex_preprocessing.regex_callable import regex_preprocessing
from text_preprocess.logic.take_scanner_tokenization.tokenizer_callable import tokenizer_preprocessing

REGEX_PARAMETERS = ['URL', 'EMAIL']
TOKENIZER_PARAMETER = ['DOC', 'CODE', 'PHONE', 'CEP', 'NUMBER']


def decision_pipeline(line_input: str, processing_parameters=[]):
    """Apply appropriate preprocessing methods.

    :param line_input: Input text to be processed.
    :type line_input: `str`
    :param processing_parameters: Preprocessing options to be applied.
    :type processing_parameters: tp.List[`str`]
    :return: Preprocessed text.
    :rtype: `str`
    """
    sentence = base_preprocessing(line_input)

    if any(parameter in processing_parameters for parameter in REGEX_PARAMETERS):
        sentence = regex_preprocessing(sentence, processing_parameters)

    if any(parameter in processing_parameters for parameter in TOKENIZER_PARAMETER):
        sentence = tokenizer_preprocessing(sentence, processing_parameters)
    return add_space_to_punctuation(sentence)
