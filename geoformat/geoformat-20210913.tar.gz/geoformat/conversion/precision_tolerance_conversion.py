import decimal


def deduce_rounding_value_from_float(float_value):
    """
    From a float value return the number of digits behind the decimal point

    :param float_value: float value
    :return: number of digits behind the decimal point
    """
    d = decimal.Decimal(str(float_value))

    return abs(d.as_tuple().exponent)


def deduce_precision_from_round(rounding_value):
    """
    From the number of digits behind the decimal return the precision associate to given number

    :param rounding_value: number of digits behind the decimal point
    :return: precision associate to input rounding_value
    """

    precision_value = (1 / 10 ** rounding_value)

    return precision_value
