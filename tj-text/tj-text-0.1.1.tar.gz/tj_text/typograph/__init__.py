from .core import TypusCore
from .mixins import EnQuotes, EnRuExpressions, RuQuotes
from .processors import EscapeHtml, EscapePhrases, Expressions

__all__ = ('en_typus', 'ru_typus')


class BaseTypus(EnRuExpressions, TypusCore):
    processors = (EscapePhrases, EscapeHtml, Expressions)


class EnTypus(EnQuotes, BaseTypus):
    """
    TODO:
    """


class RuTypus(RuQuotes, BaseTypus):
    """
    TODO:
    """


en_typus, ru_typus = EnTypus(), RuTypus()
