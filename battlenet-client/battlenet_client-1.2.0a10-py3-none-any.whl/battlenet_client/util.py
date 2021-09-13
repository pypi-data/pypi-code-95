"""
Defines utility functions for use in the battle.net rest API
"""


def currency_convertor(value):
    """Returns the value into gold, silver and copper

    Args:
        value (int or str): the value to be converted

    Returns:
        list: gold, silver and copper values
    """
    if not isinstance(value, (str, int)):
        raise TypeError("Value needs to be a string or integer")

    value = int(value)

    if value < 0:
        raise ValueError("Value must be zero or a positive value")

    return value // 10000, (value % 10000) // 100, value % 100


def slugify(value):
    """Returns the 'slugified' string

    Args:
        value (str): the string to be converted into a slug

    Returns:
        (str): the slug of :value:
    """

    if not isinstance(value, str):
        raise TypeError("Value must be a string")

    return value.lower().replace("\'", "").replace(' ', '-')


def localize(locale):
    """Returns the standardized locale

    Args:
        locale (str): the locality to be standardized

    Returns:
        (str): the locale in the format of "<lang>_<COUNTRY>"

    Raise:
        TypeError: when locale is not a string
        ValueError: when the lang and country are not in the given lists
    """
    if not isinstance(locale, str):
        raise TypeError('Locale must be a string')

    if locale[:2].lower() not in ('en', 'es', 'pt', 'fr', 'ru', 'de', 'it', 'ko', 'zh'):
        raise ValueError('Invalid language code')

    if locale[-2:].lower() not in ('us', 'mx', 'br', 'gb', 'es', 'fr', 'ru', 'de', 'pt', 'it', 'kr', 'tw', 'cn'):
        raise ValueError('Invalid country code')

    return f"{locale[:2].lower()}_{locale[-2:].upper()}"
