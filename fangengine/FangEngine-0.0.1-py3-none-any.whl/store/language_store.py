import typing
import os
import json
import locale
import ctypes

LANGUAGE_DIRECTORY = os.path.join("assets", "lang")


def get_system_lang() -> str:
    """
    Returns the LCID (Locale Identifier)

    A full list can be found here:
    https://www.science.co.il/language/Locale-codes.php
    """
    if os.name == 'posix':
        return os.environ['LANG']
    else:
        windll = ctypes.windll.kernel32
        return locale.windows_locale[windll.GetUserDefaultUILanguage()]


class LanguageStore:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LanguageStore, cls).__new__(cls)

        return cls._instance

    def set_lang(self, code: str = None):
        if code is None:
            code = get_system_lang().lower().replace("-", "_")
            self.lang_code = code[:code.index("_")]
        else:
            self.lang_code = code

        self.reload_lang_file()

    def reload_lang_file(self):
        path = os.path.join(LANGUAGE_DIRECTORY, self.lang_code.lower() + ".json")

        if not os.path.isfile(path):
            path = os.path.join(LANGUAGE_DIRECTORY, "en.json")
            self.lang_code = "en_us"

        if os.path.isfile(path):
            with open(path, 'r') as f:
                self.translations = json.loads(f.read())

        else:
            self.translations = {}
            self.lang_code = "FAILED TO LOAD"

    def __init__(self):
        self.lang_code = None
        self.translations = {}          # type: typing.Dict[str, str]

        self.set_lang()

    def __getitem__(self, item) -> str:
        return self.translations[item]

    def __len__(self):
        return len(self.translations)

    def __repr__(self):
        return "<LanguageStore code={} translations={}>".format(self.lang_code, len(self.translations))

    def __iter__(self):
        for k, v in self.translations.items():
            yield k, v
