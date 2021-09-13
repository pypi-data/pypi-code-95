from datetime import datetime


class Colours:
    BLACK = "\u001b[30m"
    RED = "\u001b[31m"
    GREEN = "\u001b[32m"
    YELLOW = "\u001b[33m"
    BLUE = "\u001b[34m"
    MAGENTA = "\u001b[35m"
    CYAN = "\u001b[36m"
    WHITE = "\u001b[37m"
    RESET = "\u001b[0m"


def printWithTime(custom_msg):
    print(
        f"{Colours.YELLOW}[ {datetime.now().strftime('%H:%M:%S.%f')[:-3]} ] - {custom_msg}{Colours.RESET}"
    )


def log(custom_msg):
    printWithTime(f"{Colours.YELLOW}{custom_msg}")


def success(custom_msg):
    printWithTime(f"{Colours.GREEN}{custom_msg}")


def error(custom_msg):
    printWithTime(f"{Colours.RED}{custom_msg}")


def warn(custom_msg):  # Warn of something that needs an action
    printWithTime(f"{Colours.MAGENTA}{custom_msg}")


def alert(custom_msg):  # Alert of something good/neutral
    printWithTime(f"{Colours.BLUE}{custom_msg}")


def msg(custom_msg):
    printWithTime(f"{Colours.CYAN}{custom_msg}")


def logp(i, custom_msg):
    log(f"[{i}] -> {custom_msg}")


def successp(i, custom_msg):
    success(f"[{i}] -> {custom_msg}")


def errorp(i, custom_msg):
    error(f"[{i}] -> {custom_msg}")


def warnp(i, custom_msg):
    warn(f"[{i}] -> {custom_msg}")


def alertp(i, custom_msg):
    alert(f"[{i}] -> {custom_msg}")


def msgp(i, custom_msg):
    msg(f"[{i}] -> {custom_msg}")
