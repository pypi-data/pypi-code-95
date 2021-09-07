# -*- coding: utf-8 -*-

# from ..convert.StringConverter import StringConverter
from typing import Any, List, Sequence

from pip_services3_commons.convert.StringConverter import StringConverter

"""
    pip_services3_commons.data.MultiString
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    MultiString implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
    
      An object that contains string translations for multiple languages.
    Language keys use two-letter codes like: 'en', 'sp', 'de', 'ru', 'fr', 'pr'.
    When translation for specified language does not exists it defaults to English ('en').
    When English does not exists it falls back to the first defined language.
  
    ### Example ###

    .. code-block:: python
  
      values = MultiString.from_tuples(
          "en", "Hello World!",
          "ru", "Привет мир!"
      );
      
      value1 = values.get('ru') # Result: "Привет мир!"
      value2 = values.get('pt') # Result: "Hello World!"
"""


class MultiString(dict):
    """
    Creates a new MultiString object and initializes it with values.
    :param language:  a map with language-text pairs.
    """

    def __init__(self, map: Any = None):
        super().__init__()
        if map:
            self.update(map)

    def get(self, language: str) -> str:
        """
        Gets a string translation by specified language.
        When language is not found it defaults to English ('en').
        When English is not found it takes the first args.

        :param language:  a language two-symbol code.
        :return: a translation for the specified language or default translation.
        """
        value = None

        try:
            # Get specified language
            value = self[language]

            # Default to english
            if value is None:
                value = self['en']
        except KeyError:
            # Default to the first property
            for language in self.keys():
                if language in self:
                    value = self[language]
                    break

        return value

    def get_languages(self) -> List[str]:
        """
        Gets all languages stored in this MultiString object,

        :return: a list with language codes.
        """
        languages = []
        for key in self.keys():
            if key in self:
                languages.append(key)
        return languages

    def put(self, language: str, value: Any):
        """

        Puts a new translation for the specified language.

        :param language: a language two-symbol code.
        :param value: a new translation for the specified language.
        """
        self[language] = StringConverter.to_nullable_string(value)

    def remove(self, language: str):
        """
        Removes translation for the specified language.

        :param language: a language two-symbol code.
        """
        self.pop(language)

    def append(self, map: Any):
        """
        Appends a map with language-translation pairs.

        :param map: the map with language-translation pairs.
        """
        if map is None:
            return self
        for key in map:
            value = map[key]
            if key in map.keys():
                self[key] = StringConverter.to_nullable_string(value)

    def clear(self) -> Any:
        """
        Clears all translations from this MultiString object.
        """
        super().clear()

    def length(self) -> int:
        """
        Returns the number of translations stored in this MultiString object.

        :return: the number of translations.
        """
        count = 0
        for key in self.keys():
            if key in self:
                count += 1
        return count

    @staticmethod
    def from_value(value: Any) -> 'MultiString':
        """
        Creates a new MultiString object from a args that contains language-translation pairs.

        :param value: the args to initialize MultiString.
        :return: a MultiString object.
        See :class:`StringValueMap <pip_services3_commons.data.StringValueMap.StringValueMap>`
        """
        return MultiString(value)

    @staticmethod
    def from_tuples(*tuples: Any) -> 'MultiString':
        """
        Creates a new MultiString object from language-translation pairs (tuples).

        :param tuples: an array that contains language-translation tuples.
        :return: a MultiString Object.
        :see :class:`from_tuples_array`
        """
        return MultiString.from_tuples_array(tuples)

    @staticmethod
    def from_tuples_array(tuples: Sequence[Any]) -> 'MultiString':
        """
        Creates a new MultiString object from language-translation pairs (tuples) specified as array.

        :param tuples: an array that contains language-translation tuples.
        :return: a MultiString Object.
        """
        result = MultiString()
        if tuples is None or len(tuples) == 0:
            return result
        index = 0
        while index < len(tuples):
            if index + 1 >= len(tuples):
                break
            name = StringConverter.to_string(tuples[index])
            value = StringConverter.to_nullable_string(tuples[index + 1])
            result[name] = value
            index += 2
        return result
