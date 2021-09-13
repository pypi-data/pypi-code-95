"""
Defines utility functions for use in the battle.net rest API
"""


def currency_convertor(value):
    """Returns the value into gold, silver and copper

    Args:
        value (int or str): the value to be converted

    Returns:
        dict: gold, silver and copper values
    """
    value = int(value)
    return {'gold': value // 10000, 'silver': (value % 10000) // 100, 'copper': value % 100}


def slugify(value):
    """Returns the 'slugified' string

    Args:
        value (str): the string to be converted into a slug

    Returns:
        (str): the slug of :value:
    """
    return value.lower().replace("\'", "").replace(' ', '-')


def localize(locale):
    """Returns the standardized locale

    Args:
        locale (str): the locality to be standardized

    Returns:
        (tuple of str): the locale <lang> and <COUNTRY>

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

    return locale[:2].lower(), locale[-2:].upper()
