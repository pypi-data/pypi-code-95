import locale


def beautify_json(value):
    if type(value) == list:
        return [beautify_json(elem) for elem in value]
    elif type(value) == dict:
        keys = list(value.keys())
        keys.sort()
        return {key: beautify_json(value[key]) for key in keys}
    else:
        return value


def number_format(num, places=0):
    return locale.format_string("%.*f", (places, num), True)


def prepare_number(number):
    exp = 18
    numb = float(number) * pow(10, exp)
    prepared_num = number_format(numb, 0)
    return prepared_num
