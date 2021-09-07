def wind(keys: list, values: list):
    return list(zip(keys, values))


def wind_to_dict(keys: list, values: list):
    return {k: v for k, v in zip(keys, values)}


def iso(keys: list, value):
    return [(key, value) for key in keys]
