"""Common functionality for analyzers."""

import abc
import functools
import unicodedata
import nltk.tokenize

_KEY_TOKEN_MIN_LENGTH = 'token_min_length'


class Analyzer(metaclass=abc.ABCMeta):
    """Base class for language-specific analyzers. The non-implemented
    methods should be overridden in subclasses. Tokenize functions may
    be overridden when necessary."""

    name = None
    token_min_length = 3  # default value, can be overridden in instances

    def __init__(self, **kwargs):
        if _KEY_TOKEN_MIN_LENGTH in kwargs:
            self.token_min_length = int(kwargs[_KEY_TOKEN_MIN_LENGTH])

    def tokenize_sentences(self, text):
        """Tokenize a piece of text (e.g. a document) into sentences."""
        return nltk.tokenize.sent_tokenize(text)

    @functools.lru_cache(maxsize=50000)
    def is_valid_token(self, word):
        """Return True if the word is an acceptable token."""
        if len(word) < self.token_min_length:
            return False
        for char in word:
            category = unicodedata.category(char)
            if category[0] == 'L':  # letter
                return True
        return False

    def tokenize_words(self, text):
        """Tokenize a piece of text (e.g. a sentence) into words."""
        return [self.normalize_word(word)
                for word in nltk.tokenize.word_tokenize(text)
                if self.is_valid_token(word)]

    @abc.abstractmethod
    def normalize_word(self, word):
        """Normalize (stem or lemmatize) a word form into a normal form."""
        pass  # pragma: no cover
