import random
from .list import normalize_list
import re

DO_NOT_CAPITALIZE = ['A', 'THE', 'OF']

HAS_ONE_UPPERCASE_REGEX = '[A-Z]'

HAS_ONE_LOWERCASE_REGEX = '[a-z]'

HAS_ONE_NUMBER_REGEX = '[0-9]'

HAS_ONE_SPECIAL_CHARACTER = '[*@!#%&()^~}{]'

LOWER_CASE_LETTERS = 'abcdefghijklmnopqrstuzwxyz'
UPPERCASE_LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
NUMBERS = '1234567890'
SPECIAL_CHARACTERS = "[*@!#%&()^~}{]"


def display(string: str) -> str:
    if string == None:
        return ''

    string_array = string.split(" ")
    formatted_string = string_array.pop(0).capitalize()
    for s in string_array:
        if s.upper() not in DO_NOT_CAPITALIZE:
            s = s.capitalize()
        else:
            s = s.lower()
        formatted_string += " "+s
    return formatted_string.strip()


def string_has_any_of(string: str, search_set: list) -> bool:
    for search_string in set(normalize_list(search_set)):
        if search_string in string:
            return True

    return False


def split(word: str) -> list:
    return [char for char in word]


def string_has_all_of(string: str, search_set: list) -> bool:
    for search_string in set(normalize_list(search_set)):
        if search_string not in string:
            return False

    return True


def get_clear_random_value(length: int = 8):
    letters = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return ''.join(random.choice(letters) for i in range(length))


def string_has_all_properties(string, with_lower=True, with_upper=False, with_number=False, with_special=False):
    if with_lower and not string_has_any_of(string, split(LOWER_CASE_LETTERS)):
        return False

    if with_upper and not string_has_any_of(string, split(UPPERCASE_LETTERS)):
        return False

    if with_number and not string_has_any_of(string, split(NUMBERS)):
        return False

    if with_special and not string_has_any_of(string, split(SPECIAL_CHARACTERS)):
        return False

    return True


def get_random_string(
        length: int = 12,
        with_lower: bool = True,
        with_upper: bool = False,
        with_number: bool = False,
        with_special: bool = False,
        max_tires: int = 100000) -> str:
    if length < 1:
        raise ValueError("Length cannot be less then one")

    letters = ''
    minimum_length = 0

    if with_lower:
        letters += LOWER_CASE_LETTERS
        minimum_length = minimum_length + 1

    if with_upper:
        letters += UPPERCASE_LETTERS
        minimum_length = minimum_length + 1

    if with_number:
        letters += NUMBERS
        minimum_length = minimum_length + 1

    if with_special:
        letters += SPECIAL_CHARACTERS
        minimum_length = minimum_length + 1

    if len(letters) == 0:
        raise ValueError("Random string requires true requirement")
    elif length < minimum_length:
        raise ValueError(
            "Random string of those requirement and length cannot be generated")

    def get_random():
        return ''.join(random.choice(letters) for i in range(length))

    def has_all_required_params():
        return string_has_all_properties(
            possible_string,
            with_lower,
            with_upper,
            with_number,
            with_special
        )

    generation_tries = 1
    possible_string = get_random()
    while not has_all_required_params() and generation_tries < max_tires:
        generation_tries += 1
        possible_string = get_random()

    if has_all_required_params():
        return possible_string
    else:
        raise ValueError("String could not be successfully generated")


def camel_case_split(str: str) -> str:
    words = [[str[0]]]

    for c in str[1:]:
        if words[-1][-1].islower() and c.isupper():
            words.append(list(c))
        else:
            words[-1].append(c)

    return " ".join(map(lambda w: w.title(), [''.join(word) for word in words]))


def camel_case_to_slug(s: str) -> str:
    return camel_case_split(s).replace(" ", "_").lower()


def represents_int(s: str, fail_safely: str = True) -> bool:
    try:
        int(s)
        return True
    except ValueError:
        if fail_safely:
            return False
        raise ValueError


def validation_check(input_string: str, regex: str) -> bool:
    if re.search(regex, input_string):
        return True
    else:
        return False

def dash_case_to_upper_slug(s : str) -> str:
    if s == None:
        return None
    
    return s.upper().replace("-", '_')
