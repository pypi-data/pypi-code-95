import logging
import typing

from colorama import Fore, Back, Style


def property_input(prompt: str, alt: typing.Any = None) -> typing.Optional[str]:
    inp = input(Back.WHITE + f"[{prompt}] ({alt}):" + Style.RESET_ALL + " ")
    if inp == "":
        return alt
    return inp


def required_property_input(prompt: str) -> str:
    def print_prompt() -> str:
        return input(
            f"{Back.WHITE}[{Fore.RED}*{Fore.RESET}{prompt}]:{Style.RESET_ALL} "
        )

    inp = print_prompt()
    while inp.strip() == "":
        inp = print_prompt()
    return inp


def header(heading: str) -> None:
    print(Back.LIGHTBLUE_EX + Style.BRIGHT + "   " + heading + "   " + Style.RESET_ALL)


def fatal_error(message: str) -> None:
    logging.exception(message)
    print(Back.RED + Style.BRIGHT + message + Style.RESET_ALL)


def sudden_exit():
    print("\nExiting meed!")
