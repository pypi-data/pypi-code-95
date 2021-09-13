""" This module provides a function to generate a quick custom sized password. """

import random
import string


def generator():
    """ 
    Generate a user-inputted sized length password.

    Parameters: 
    - NIL -

    Returns:
    str : generated password.
    """

    flag = 1
    while flag:
        password_len = input(
            "Enter the length of password characters you require to generate: ")
        if password_len.isalpha() or not password_len.isnumeric():
            print("Enter a Numeric value.")
        elif int(password_len) <= 0 or len(password_len) == 0:
            print("Enter atleast one value more than 'Zero'")
        else:
            password = "".join(random.choices(string.ascii_letters +
                                              string.digits + "!@#$%^&*()_", k=int(password_len)))
            flag = 0

    return password
