import math
import random
import time

from .constants import TYPE_EFFECTS
from .text_display import (
    show_health_bar,
    clear_screen,
    display_text,
)


def choose_move(player_pokemon):
    """
    Choose one of the 4 moves
    """
    is_move_selected = False
    display_text(text="Choose your move: \n")
    for count, move in enumerate(player_pokemon.moveset):
        display_text(
            text=f"{count + 1} : {move} \n \t "
            + f"{move.stats['pp_left']}/{move.stats['total_pp']}",
        )
        time.sleep(0.2)
    display_text(text="")
    while not is_move_selected:
        selected_move_string = display_text(
            text="Choose your move [1-4]: ",
            user_input=True,
            include_arrow=False,
            animate=True,
        )
        possible_selections = [str(move_no) for move_no in range(1, 5)]
        if selected_move_string in possible_selections:
            selected_move = int(selected_move_string) - 1
            if player_pokemon.moveset[selected_move].stats["pp_left"] > 0:
                player_pokemon.moveset[selected_move].stats["pp_left"] -= 1
                is_move_selected = True
            else:
                display_text(text="There's no PP left", user_input=True, animate=True)
        else:
            display_text(text="Invalid move choice", user_input=True, animate=True)
    return selected_move


def damage_function(variables):
    """
    The damage that the attacking pokemon inflicts to the defending pokemon.
    The formula is as described by:
    https://www.math.miami.edu/~jam/azure/compendium/battdam.htm

    The variable dictionary has the following keys
    ----------
    level : int
        Attacker's level by default 50
    attack : int
        Attacker's attack stat
    power : int
        Power of the move
    defender_defense : int
        Defender's defense stat
    same_type : boolean
        True if move type is the same type as the attacking pokemon
    modifier : int, optional
        Modifier based on type effectveness, by default 10
    stochastic : int, optional
        A random number, by default random.randint(217, 255)
    """
    stab = 1.5 if variables["same_type_advantage"] else 1

    damage = math.floor((2 * variables["attacker_level"] / 5) + 2)
    damage *= variables["attacker_attack"] * variables["move_power"]
    damage = math.floor(damage / variables["defender_defense"])
    damage = math.floor(damage / 50)
    damage = math.floor(damage * stab)
    damage = math.floor(damage * variables["modifier"])
    damage *= variables["stochasticity"]
    damage /= 255

    return math.floor(damage)


def apply_move(attacking_pokemon, defending_pokemon, move):
    """
    Apply the move to the enemy pokemon
    """

    attack_variables = {}
    attack_variables["move_power"] = attacking_pokemon.moveset[move].stats["power"]
    attack_variables["move_type"] = attacking_pokemon.moveset[move].stats["type"]

    attack_variables["attacker_level"] = 50
    attack_variables["attacker_type"] = attacking_pokemon.type
    attack_variables["attacker_attack"] = attacking_pokemon.stats["attack"]

    attack_variables["defender_defense"] = defending_pokemon.stats["defense"]
    defender_type = defending_pokemon.type

    attack_variables["same_type_advantage"] = (
        attack_variables["move_type"] in attack_variables["attacker_type"]
    )
    type_effects = list(
        TYPE_EFFECTS[attack_variables["move_type"]][type_i] for type_i in defender_type
    )
    attack_variables["modifier"] = math.prod(type_effects)
    attack_variables["stochasticity"] = random.randint(217, 255)

    display_text(
        text=f"{attacking_pokemon} used {attacking_pokemon.moveset[move]}",
        user_input=True,
        animate=True,
    )
    if attack_variables["move_power"] is not None:
        damage = damage_function(variables=attack_variables)
        move_accuracy = (
            attacking_pokemon.moveset[move].stats["accuracy"]
            if attacking_pokemon.moveset[move].stats["accuracy"] is not None
            else 100
        )

        if random.random() < (move_accuracy / 100):
            defending_pokemon.health_points = defending_pokemon.health_points - damage
            if attack_variables["modifier"] == 1:
                display_text(
                    text=f"It's effective! (Damage: {damage})",
                    user_input=True,
                    animate=True,
                )
            elif attack_variables["modifier"] >= 2:
                display_text(
                    text=f"It's super effective! (Damage: {damage})",
                    user_input=True,
                    animate=True,
                )
            elif 0 < attack_variables["modifier"] <= 0.5:
                display_text(
                    text=f"It's not very effective! (Damage: {damage})",
                    user_input=True,
                    animate=True,
                )
            elif attack_variables["modifier"] == 0:
                display_text(
                    text=f"But it failed! (Damage: {damage})",
                    user_input=True,
                    animate=True,
                )
            else:
                raise ValueError("Invalid modifier value")
        else:
            display_text(text="Attack missed!", user_input=True, animate=True)
    else:
        display_text(
            text="Unfortunately this move has not been implemented yet. Sorry.",
            user_input=True,
            animate=True,
        )

    if defending_pokemon.health_points <= 0:
        display_text(text=f"{defending_pokemon} fainted", user_input=True, animate=True)
        defending_pokemon.health_points = 0
        defending_pokemon.stats = "inactive"

    return defending_pokemon.health_points


def player_turn_logic(player_pokemon, enemy_pokemon, enemy_remaining_pokemon):
    """
    Logic of the player turn
    """
    display_text(text=f"{player_pokemon} 's turn", user_input=True, animate=True)
    selected_move = choose_move(player_pokemon)
    apply_move(player_pokemon, enemy_pokemon, selected_move)
    if enemy_pokemon.health_points <= 0:
        enemy_remaining_pokemon.remove(enemy_pokemon)
        if len(enemy_remaining_pokemon) > 0:
            enemy_pokemon = enemy_remaining_pokemon[0]
            clear_screen()
            show_health_bar(pokemon_1=player_pokemon, pokemon_2=enemy_pokemon)
            print("\n")
            display_text(
                text=f"Enemy chooses {enemy_pokemon}", user_input=True, animate=True
            )
    return enemy_pokemon, enemy_remaining_pokemon


def enemy_turn_logic(player_pokemon, enemy_pokemon, player_remaining_pokemon):
    """
    Logic of the enemy turn
    """
    display_text(text=f"{enemy_pokemon} 's turn", user_input=True, animate=True)
    enemy_move = random.randint(0, len(enemy_pokemon.moveset) - 1)
    apply_move(enemy_pokemon, player_pokemon, enemy_move)
    if player_pokemon.health_points <= 0:
        player_remaining_pokemon.remove(player_pokemon)
        if len(player_remaining_pokemon) > 0:
            clear_screen()
            show_health_bar(pokemon_1=player_pokemon, pokemon_2=enemy_pokemon)
            print("\n")
            display_text("Which pokemon do you choose?")
            for i, poke in enumerate(player_remaining_pokemon):
                display_text(text=f"{i + 1} :  {poke}")
            is_pokemon_selected = False
            while not is_pokemon_selected:
                poke_choice_string = display_text(
                    text="Choose a pokemon: ",
                    user_input=True,
                    animate=True,
                    include_arrow=False,
                )
                possible_selections = [
                    str(poke_no)
                    for poke_no in range(1, len(player_remaining_pokemon) + 1)
                ]
                if poke_choice_string in possible_selections:
                    is_pokemon_selected = True
                    poke_choice = int(poke_choice_string) - 1
                    player_pokemon = player_remaining_pokemon[poke_choice]
                else:
                    display_text(
                        text="Invalid pokemon choice", user_input=True, animate=True
                    )
            clear_screen()
            show_health_bar(pokemon_1=player_pokemon, pokemon_2=enemy_pokemon)
    return player_pokemon, player_remaining_pokemon
