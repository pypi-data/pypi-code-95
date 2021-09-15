import os
import sys
import inspect
from .DEFAULT import DEFAULT_NICKNAME
from .QuestionSource import Source

# Abstraction - element with the data data for all question abstraction like (question, comment, answer)
class QuestionElement:
    # Site from QuestionSource enumeration.
    Source = Source.StackOverflow

    # Nickname of user that made element.
    Nickname = 'DEFAULT_NICKNAME'

    # Date of the element creation.
    Date = None

    # Content which user have created.
    Content = ''

    # Default rating from source.
    Rating = 0

    # Rating calculated rating based on special formula -
    # - it needs to equalize all stats from different sources.
    GeneralRating = 0

    def __init__(self, nick, date, content, rating):
        self.Nickname = nick
        self.Date = date
        self.Content = content
        self.Rating = rating


