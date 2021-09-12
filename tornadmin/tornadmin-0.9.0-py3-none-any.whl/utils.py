import re
import unicodedata
import datetime


# Taken from: https://stackoverflow.com/a/41510011/1925257
RE_CAMEL = re.compile(r'''
        # Find words in a string. Order matters!
        [A-Z]+(?=[A-Z][a-z]) |  # All upper case before a capitalized word
        [A-Z]?[a-z]+ |  # Capitalized words / all lower case
        [A-Z]+ |  # All upper case
        \d+  # Numbers
    ''',
    re.VERBOSE
)

def split_camel(value):
    return RE_CAMEL.findall(value)


def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.

    Copied from django.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


def get_display_name(value):
    return ' '.join(value.split('_')).capitalize()


def get_value(variable):
    """If the variable is a callable, it will be called.
    
    :TODO: If the variable is a date or datetime object, it will
    return formatted result.

    This is useful in templates to avoid having to check
    whether a variable is callable or not.
    """
    if callable(variable):
        return variable()

    return variable