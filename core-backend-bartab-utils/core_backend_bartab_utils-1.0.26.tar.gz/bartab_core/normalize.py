from .string import camel_case_to_slug, display
from .list import normalize_list


def map_to_slug_keys(map_value):
    new_map_value = {}
    for key in map_value:
        if isinstance(map_value[key], dict):
            new_map_value[camel_case_to_slug(
                key)] = map_to_slug_keys(map_value[key])
        else:
            new_map_value[camel_case_to_slug(key)] = map_value[key]
    return new_map_value


def map_values(
        map_value: dict,
        keys_to_exchange: dict,
        override_existing: bool = True) -> dict:

    for existing_key in keys_to_exchange:
        if existing_key in map_value:
            new_key = keys_to_exchange[existing_key]

            if new_key not in map_value or override_existing:
                map_value[new_key] = map_value[existing_key]
                del map_value[existing_key]

    return map_value


class NormalizedBool:
    VALID_EXACT_TRUE_STRING = 'TRUE'
    VALID_EXACT_FALSE_STRING = 'FALSE'

    VALID_TRUE_STRINGS = ['T', VALID_EXACT_TRUE_STRING, 'YES', 'Y', '1']
    VALID_FALSE_STRINGS = [
        'F', VALID_EXACT_FALSE_STRING, 'NO', 'N', '0', 'NONE']

    def __init__(self, value, default_exact_equivalency=False):
        self.__sent_value = value
        value = str(value).upper()
        self.__is_valid = True
        self.__default_exact_equivalency = default_exact_equivalency

        self.__is_valid_exact = (
            value == self.VALID_EXACT_TRUE_STRING or value == self.VALID_EXACT_FALSE_STRING)

        if value in self.VALID_TRUE_STRINGS:
            self.__bool_value = True
        elif value in self.VALID_FALSE_STRINGS:
            self.__bool_value = False
        else:
            self.__is_valid = False

    def get_error_message(self, exact=None):
        exact = exact if exact != None else self.__default_exact_equivalency

        if exact and not self.__is_valid_exact:
            return "Strict equivalency is being enforced for this method. {} is not True or False".format(self.__sent_value)
        elif not exact and not self.__is_valid:
            return "{} is not a valid value. Valid values are: {}".format(self.__sent_value, ", ".join(
                (
                    self.VALID_TRUE_STRINGS + self.VALID_FALSE_STRINGS
                )
            ))
        else:
            return None

    def is_valid(self, exact=None):
        exact = exact if exact != None else self.__default_exact_equivalency

        return self.__is_valid_exact if exact else self.__is_valid

    def get(self, exact=None):
        exact = exact if exact != None else self.__default_exact_equivalency

        if not self.is_valid(exact):
            raise ValueError({"bool": self.get_error_message(exact)})

        return self.__bool_value


class NomalizedString:

    def __init__(self, value, valid_values, default_exact_equivalency=False):
        self.sent_value = value
        self.__valid_values = normalize_list(valid_values)
        self.__default_exact_equivalency = default_exact_equivalency

    def is_valid(self, exact=None):
        exact = exact if exact != None else self.__default_exact_equivalency

        if exact:
            return self.sent_value in self.__valid_values
        else:
            return self.sent_value.lower() in list(map(lambda s: s.lower(), self.__valid_values))

    def get_valid_value(self):
        for valid_value in self.__valid_values:
            if valid_value.lower() == self.sent_value.lower():
                return valid_value
        raise ValueError(f"{self.sent_value} is not a valid value")
