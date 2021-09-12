from art import text2art
from termcolor import colored

from ...utils.strings.formatters import heading, notice

TITLE = "\n" + colored(text2art("templ8", "ghost"), "blue")

RECEIVED_INPUTS = heading(
    "Received inputs.",
    [1, 4],
    "wrapped_gift",
)

GATHERING_COLLECTIONS = heading(
    "Gathering collections.",
    [2, 4],
    "notebook_with_decorative_cover",
)

INTROSPECTING_STATE = heading(
    "Introspecting state.",
    [3, 4],
    "woman_scientist",
)

APPLYING_MUTATIONS = heading(
    "Applying mutations.",
    [4, 4],
    "speedboat",
)

PLUG = notice(
    "Templ8's author JoelLefkowitz is looking for a good job!",
    ["spade_suit", "red_heart"],
)
