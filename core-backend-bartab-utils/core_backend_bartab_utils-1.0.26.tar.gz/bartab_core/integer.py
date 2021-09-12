from .float import is_float, get_float_decimal

def int_value_or_none(possible_int):
    try:
        return int(possible_int)
    except ValueError:
        return None

def is_int(possible_int_number):
    valid_float = is_float(possible_int_number)

    if not valid_float:
        return False
    else:
        return get_float_decimal(float(possible_int_number)) == 0