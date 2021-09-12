import re
import shortuuid
from .string import split
from .integer import int_value_or_none


def valid_string_of_length(string, length: int):
    if string == None or not isinstance(string, str):
        return False
    
    length_value = int_value_or_none(length)
    
    if length_value == None:
        raise ValueError("length must be type int")
    else:
        return len(string) == length_value

def is_valid_uuid(uuid):
    if not valid_string_of_length(uuid, 36):
        return False
    else:
        regex = re.compile(
            "^[{]?[0-9a-fA-F]{8}" + "-([0-9a-fA-F]{4}-)" + "{3}[0-9a-fA-F]{12}[}]?$")

        return bool(re.search(regex, uuid))

def is_valid_short_uuid(uuid):
    if not valid_string_of_length(uuid, 22):
        return False
    else:
        valid_short_uuid_chars = shortuuid.get_alphabet()

        for uuid_char in split(uuid):
            if uuid_char not in valid_short_uuid_chars:
                return False
        return True