def normalize_list(value):
    if value == None:
        return []
    
    if type(value) is not list:
        return [value]
    else:
        return value


def comma_seperated_string_to_list(value: str):
    return list(map(lambda x: x.strip(), value.split(",")))


def valid_comma_seperated_list(values: str, valid_values: list):
    for value in comma_seperated_string_to_list(values):
        if value not in valid_values:
            return False
    return True
