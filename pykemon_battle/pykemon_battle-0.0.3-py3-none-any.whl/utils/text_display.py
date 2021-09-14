import os
import sys
import time

import numpy as np
from rich.console import Console


def show_health_bar(pokemon_1, pokemon_2):
    """
    Function to display health points of the battling pokemon
    """
    bar_1_length = int(np.ceil(pokemon_1.health_points / 3))
    bar_2_length = int(np.ceil(pokemon_2.health_points / 3))
    health_text_1, health_text_2 = (
        f"HP: {pokemon_1.health_points}/{pokemon_1.json['stats'][0]['base_stat']} ",
        f"HP: {pokemon_2.health_points}/{pokemon_2.json['stats'][0]['base_stat']} ",
    )
    health_bar_1, health_bar_2 = "", ""
    for _ in range(bar_1_length):
        health_bar_1 += "#"
    for _ in range(bar_2_length):
        health_bar_2 += "#"
    display_text(text=pokemon_1)
    display_text(text=health_bar_1)
    display_text(text=health_text_1)
    display_text(text="")
    display_text(text=pokemon_2)
    display_text(text=health_bar_2)
    display_text(text=health_text_2)


def clear_screen():
    """
    Function to clear the terminal
    """
    os.system("cls" if os.name == "nt" else "clear")


def animate_text(console, text):
    """
    Function to animate text
    """
    delay = 0.15 / len(text)
    for character in str(text) + " ":
        console.print(character, end="")
        sys.stdout.flush()
        time.sleep(delay)


def display_text(
    text,
    user_input=False,
    animate=False,
    style="bold white on black",
    include_arrow=True,
):
    """
    Function to display text in the terminal
    """
    if user_input:
        custom_end = " "
    else:
        custom_end = "\n"
    py_console = Console(highlight=False, style=style)
    if animate:
        animate_text(console=py_console, text=text)
    else:
        py_console.print(text, end=custom_end)
    if user_input:
        if include_arrow:
            out = py_console.input("▼")
        else:
            out = py_console.input("")
        py_console.print("\033[A", " " * (len(text) + 2), "\033[A")
        return out
    return None
