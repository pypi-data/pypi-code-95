def get_float_decimal(float_number):
    float_string = str(float_number)

    if "." in float_string:
        decimal_length = len(float_string.split(".")[1])
        return round(float_number-int(float_number),decimal_length) 
    else:
        return 0


def is_float(possible_float_number):
    try:
        float(possible_float_number)
        return True
    except:
        return False