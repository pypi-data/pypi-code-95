from functools import lru_cache
from collections import Counter
import argparse


@lru_cache(maxsize=32)
def amount_of_unique_char(string: str)->tuple:
    dict_of_char = Counter(string)
    list_unique_char = [value for value, count in dict_of_char.items() if count == 1]
    amount_unique = len(list_unique_char)
    return amount_unique, list_unique_char


def format_return(input_string: str)->str:
    amount, list_unique = amount_of_unique_char(input_string)
    if amount == 0:
        return f'"{input_string}" => {amount}' + '\n' + "none" + " are present once."
    else:
        return f'"{input_string}" => {amount}' + '\n' + ",".join(list_unique) + " are present once."


def cli(**args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="get file and return amount of unique char from text" +
                                       "syntax: --file <path_to_your_file>")
    parser.add_argument("--string", help="return amount of unique char from input string" +
                                         "syntax: --string <your_string>")
    return parser.parse_args(**args)


def work_with_args(file: bytes, string: str)->str:
    if file:
        try:
            with open(file, 'r') as f:
                return ''.join(list(map(str.strip, f.readlines())))
        except FileNotFoundError:
            raise FileNotFoundError('file not found')
    elif string:
        return string