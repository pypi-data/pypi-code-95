import os
from .constants import TERMINAL_BACKGROUND_CORRECTIONS


def change_terminal_background(pokemon):
    """
    Change the terminal background based on the pokemon's name.
    """
    if pokemon.json["id"] <= 719:
        corrected_poke_name = pokemon.name
        if pokemon.name in TERMINAL_BACKGROUND_CORRECTIONS:
            corrected_poke_name = TERMINAL_BACKGROUND_CORRECTIONS[pokemon.name]
        os.system(f"pokemon {corrected_poke_name}")
