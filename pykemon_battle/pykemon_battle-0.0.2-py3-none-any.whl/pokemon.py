from .utils.utilities import (
    get_pokemon_info,
    choose_best_moveset,
    randomly_choose_moveset,
    manually_choose_moveset,
    choose_first_four_moves_for_now,
)

from .move import Move


class Pokemon:
    """
    A pokemon is a class that represents a pokemon.
    """

    def __init__(self, poke_id):
        self.json = get_pokemon_info(poke_id=poke_id)
        self.name = self.json["name"]
        self.type = list(slot["type"]["name"] for slot in self.json["types"])
        self.heal()
        self.reset()
        self.moveset = None

        # self.get_moves()

    def reset(self):
        """
        Resets the pokemon's health points to its base stat.
        """
        attack = self.json["stats"][1]["base_stat"]
        defense = self.json["stats"][2]["base_stat"]
        special_attack = self.json["stats"][3]["base_stat"]
        special_defense = self.json["stats"][4]["base_stat"]
        speed = self.json["stats"][5]["base_stat"]
        self.stats = {
            "attack": attack,
            "defense": defense,
            "special_attack": special_attack,
            "special_defense": special_defense,
            "speed": speed,
        }

    def heal(self):
        """
        Heals the pokemon to its base stat.
        """
        self.health_points = self.json["stats"][0]["base_stat"]
        self.status = "active"

    def get_moves(self, move_selection="Random"):
        """
        Returns a list of moves that the pokemon can use.
        """
        all_possible_moves = self.json["moves"]
        if move_selection == "1" or move_selection.lower() == "automatic":
            selected_moves = choose_best_moveset(all_possible_moves)
        elif move_selection == "2" or move_selection.lower() == "manual":
            selected_moves = manually_choose_moveset(all_possible_moves)
        elif move_selection == "3" or move_selection.lower() == "random":
            selected_moves = randomly_choose_moveset(all_possible_moves)
        else:
            selected_moves = choose_first_four_moves_for_now(all_possible_moves)

        self.moveset = (
            Move(selected_moves[0]),
            Move(selected_moves[1]),
            Move(selected_moves[2]),
            Move(selected_moves[3]),
        )

    def __repr__(self):
        return f"{self.name.capitalize()}"


# demo_poke = Pokemon("Silcoon")
# demo_poke.get_moves()
