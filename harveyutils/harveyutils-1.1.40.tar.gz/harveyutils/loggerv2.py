from datetime import datetime


class Colours:
    black = "\u001b[30m"
    red = "\u001b[31m"
    green = "\u001b[32m"
    yellow = "\u001b[33m"
    blue = "\u001b[34m"
    magenta = "\u001b[35m"
    cyan = "\u001b[36m"
    white = "\u001b[37m"
    reset = "\u001b[0m"


def make_camel_case(string):
    string_split = string.split(" ")
    for index, word in enumerate(string.split(" ")):
        uppercase_char_count = 0

        if word.startswith("https://") or word.startswith("www."):
            continue

        for char in word:
            if char.isupper():
                uppercase_char_count += 1

        if len(word) == 0:
            uppercase_char_percantage = 100
        else:
            uppercase_char_percantage = uppercase_char_count / len(word) * 100

        if uppercase_char_percantage < 50:
            string_split[index] = f"{word[0].upper()}{word[1:]}"

    new_string = " ".join(string_split)
    return new_string


def appendTime(string):
    """Appends a time string (in yellow) to a string in the format: [ 21:47:32.344 ] - string

    Arguements:
        string:String -- A string to append to the time

    Returns:
        String -- Formatted string: [ 21:47:32.344 ] - string
    """
    return f"{Colours.yellow}[ {datetime.now().strftime('%H:%M:%S.%f')[:-3]} ] - {string}{Colours.reset}"


def formatString(string, prefix, colour_code, should_camel_case):
    """Returns a formatted string based on args.

    Arguements:
        string:String -- A string to print to the console
        colour_code:String -- A colour code?
        prefix:String -- A prefix to be appended to the main string in the format [prefix] -> string
            or an empty string for no prefix.
        should_camel_case:Boolean -- If set to true will reformat log content to camel case

    Returns:
        String -- A formatted string based on provided args.
    """
    string = str(string)

    if should_camel_case:
        string = make_camel_case(string)

    if prefix:
        string = f"[{prefix}] -> {string}"

    colour_string = f"{colour_code}{string}"
    coloured_formatted_string = appendTime(colour_string)

    return coloured_formatted_string


class Logger:
    """Logger class to print to the console with formatting.

    Attributes:
        should_camel_case:Boolean -- If set to true will reformat log content to camel case
        main_prefix:String -- A prefix that will repalce all other prefixes and always be appended to
            the string arguement.
    """

    def __init__(self, should_camel_case=False, main_prefix=""):
        self.should_camel_case = should_camel_case
        self.main_prefix = main_prefix

    def print_formatted(self, string, prefix, colour):
        print(formatString(string, prefix, colour, self.should_camel_case))

    def log(self, string, prefix=""):
        """Used for general logs. Prints to the console formatted with YELLOW colour.

        Arguements:
            string:String -- A string to print to the console
            prefix:String -- A string to append to the main string in the format: [prefix] -> string
                this will be replaced if self.main_string is not an empty string.
        """
        if self.main_prefix:
            self.print_formatted(string, self.main_prefix, Colours.yellow)
        else:
            self.print_formatted(string, prefix, Colours.yellow)

    def success(self, string, prefix=""):
        """Used for successful logs. Prints to the console formatted with GREEN colour.

        See .log()
        """
        if self.main_prefix:
            self.print_formatted(string, self.main_prefix, Colours.green)
        else:
            self.print_formatted(string, prefix, Colours.green)

    def error(self, string, prefix=""):
        """Used for error logs. Prints to the console formatted with RED colour.

        See .log()
        """
        if self.main_prefix:
            self.print_formatted(string, self.main_prefix, Colours.red)
        else:
            self.print_formatted(string, prefix, Colours.red)

    def warn(self, string, prefix=""):
        """Used for when the user needs to be warned of something where an action needs to be taken.
        Prints to the console formatted with MAGENTA colour.

        See .log()
        """
        if self.main_prefix:
            self.print_formatted(string, self.main_prefix, Colours.magenta)
        else:
            self.print_formatted(string, prefix, Colours.magenta)

    def alert(self, string, prefix=""):
        """Used for when the user needs to be alerted of something but no action needs to be taken.
        Prints to the console formatted with MAGENTA colour.

        See .log()
        """
        if self.main_prefix:
            self.print_formatted(string, self.main_prefix, Colours.blue)
        else:
            self.print_formatted(string, prefix, Colours.blue)

    def msg(self, string, prefix=""):
        """Used for when you want to show a message that should stand out usually after one off actions are completed.
        Prints to the console formatted with CYAN colour.

        See .log()
        """
        if self.main_prefix:
            self.print_formatted(string, self.main_prefix, Colours.cyan)
        else:
            self.print_formatted(string, prefix, Colours.cyan)
