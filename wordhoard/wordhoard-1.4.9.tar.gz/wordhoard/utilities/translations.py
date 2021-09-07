
import logging
from deep_translator import GoogleTranslator
from deep_translator import LingueeTranslator
from deep_translator.exceptions import ElementNotFoundInGetRequest

logger = logging.getLogger(__name__)


class LanguageTranslations(object):
    """
    This class is used to translate a specific word from its original language
    to American English.

    """

    def __init__(self, search_string=None, source_language=None, translations_type=None):
        """
        Usage Examples
        ----------

        >>> translate = LanguageTranslations(search_string='madre', source_language='spanish')

        Parameters
        ----------
        :param search_string: string containing the variable to translate
        :param source_language:
        :param translations_type:
        """
        self._word = search_string
        self._translations_type = translations_type
        self._source_language = source_language

    def _linguee_supported_languages(self):
        """

        :return:
        """
        # Linguee Translator supported languages listed in deep_translator as of 09-03-2021
        # source: https://github.com/nidhaloff/deep-translator/blob/master/deep_translator/constants.py
        supported_languages = {'bg': 'bulgarian', 'zh': 'chinese', 'cs': 'czech', 'da': 'danish',
                               'nl': 'dutch', 'en': 'english', 'et': 'estonian', 'fi': 'finnish',
                               'fr': 'french', 'de': 'german', 'el': 'greek', 'hu': 'hungarian',
                               'it': 'italian',  'ja': 'japanese', 'lo': 'laotian', 'lv': 'latvian',
                               'mt': 'maltese', 'pl': 'polish', 'pt': 'portuguese', 'ro': 'romanian',
                               'ru': 'russian',  'sk': 'slovakian', 'sl': 'slovenian', 'es': 'spanish',
                               'sv': 'swedish'}
        if self._source_language in supported_languages.keys():
            return self._source_language
        elif self._source_language in supported_languages.values():
            return self._source_language
        else:
            return None

    def _linguee_translations_inital(self):
        """

        :return:
        """
        original_language = self._linguee_supported_languages()
        if original_language:
            try:
                translated_word = LingueeTranslator(source=original_language, target='english').translate(self._word)
                print(translated_word)
            except ElementNotFoundInGetRequest:
                print('here')
        else:
            logger.info('The language provided is not one supported by the Linguee Translator.')
            return 'The language provided is not one supported by the Linguee Translator.'

    def _google_supported_languages(self):
        """

        :return:
        """
        # Google Translator supported languages listed in deep_translator as of 09-03-2021
        # source: https://github.com/nidhaloff/deep-translator/blob/master/deep_translator/constants.py
        supported_languages = {'af': 'afrikaans', 'sq': 'albanian', 'am': 'amharic', 'ar': 'arabic', 'hy': 'armenian',
                              'az': 'azerbaijani', 'eu': 'basque', 'be': 'belarusian', 'bn': 'bengali', 'bs': 'bosnian',
                              'bg': 'bulgarian', 'ca': 'catalan', 'ceb': 'cebuano', 'ny': 'chichewa',
                              'zh-CN': 'chinese (simplified)', 'zh-TW': 'chinese (traditional)', 'co': 'corsican',
                              'hr': 'croatian', 'cs': 'czech', 'da': 'danish', 'nl': 'dutch', 'en': 'english',
                              'eo': 'esperanto', 'et': 'estonian', 'tl': 'filipino', 'fi': 'finnish', 'fr': 'french',
                              'fy': 'frisian', 'gl': 'galician', 'ka': 'georgian', 'de': 'german', 'el': 'greek',
                              'gu': 'gujarati', 'ht': 'haitian creole', 'ha': 'hausa', 'haw': 'hawaiian',
                              'iw': 'hebrew', 'hi': 'hindi', 'hmn': 'hmong', 'hu': 'hungarian', 'is': 'icelandic',
                              'ig': 'igbo', 'id': 'indonesian', 'ga': 'irish', 'it': 'italian', 'ja': 'japanese',
                              'jw': 'javanese', 'kn': 'kannada', 'kk': 'kazakh', 'km': 'khmer', 'rw': 'kinyarwanda',
                              'ko': 'korean', 'ku': 'kurdish', 'ky': 'kyrgyz', 'lo': 'lao', 'la': 'latin',
                              'lv': 'latvian', 'lt': 'lithuanian', 'lb': 'luxembourgish', 'mk': 'macedonian',
                              'mg': 'malagasy', 'ms': 'malay', 'ml': 'malayalam', 'mt': 'maltese', 'mi': 'maori',
                              'mr': 'marathi', 'mn': 'mongolian', 'my': 'myanmar', 'ne': 'nepali', 'no': 'norwegian',
                              'or': 'odia', 'ps': 'pashto', 'fa': 'persian', 'pl': 'polish', 'pt': 'portuguese',
                              'pa': 'punjabi', 'ro': 'romanian', 'ru': 'russian', 'sm': 'samoan', 'gd': 'scots gaelic',
                              'sr': 'serbian', 'st': 'sesotho', 'sn': 'shona', 'sd': 'sindhi', 'si': 'sinhala',
                              'sk': 'slovak', 'sl': 'slovenian', 'so': 'somali', 'es': 'spanish', 'su': 'sundanese',
                              'sw': 'swahili', 'sv': 'swedish', 'tg': 'tajik', 'ta': 'tamil', 'tt': 'tatar',
                              'te': 'telugu', 'th': 'thai', 'tr': 'turkish', 'tk': 'turkmen', 'uk': 'ukrainian',
                              'ur': 'urdu', 'ug': 'uyghur', 'uz': 'uzbek', 'vi': 'vietnamese', 'cy': 'welsh',
                              'xh': 'xhosa', 'yi': 'yiddish', 'yo': 'yoruba', 'zu': 'zulu'}

        if self._source_language in supported_languages.keys():
            return self._source_language
        elif self._source_language in supported_languages.values():
            return self._source_language
        else:
            return None

    def _google_translations_inital(self):
        """

        :return:
        """
        original_language = self._google_supported_languages()
        if original_language:
            try:
                translated_word = GoogleTranslator(source=original_language, target='english').translate(self._word)
                return translated_word
            except ElementNotFoundInGetRequest:
                print('here')
        else:
            logger.info('The language provided is not one supported by the Google Translator.')
            return 'The language provided is not one supported by the Google Translator.'

    def _google_translations_reverse(self):
        """

        :return:
        """
        try:
            translated_word = GoogleTranslator(source='english', target=self._source_language).translate(self._word)
            return translated_word
        except ElementNotFoundInGetRequest:
                print('here')

    def translate_word(self):
        if self._translations_type.lower() == 'google':
            return self._google_translations_inital()
        elif self._translations_type.lower() == 'linguee':
            self._linguee_translations_inital()
        else:
            print('try again')


    def reverse_translate(self):
        return self._google_translations_reverse()



word = LanguageTranslations('madre', 'es', 'google').translate_word()
print(word)
test = LanguageTranslations(word, 'es').reverse_translate()
print(test)