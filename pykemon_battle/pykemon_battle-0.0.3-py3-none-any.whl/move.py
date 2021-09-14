from .utils.utilities import get_move_info


class Move:
    """
    A move class that contains all the information about a move.
    """

    def __init__(self, move_name):
        self.json = get_move_info(move_name)
        self.name = self.json["name"]
        move_type = self.json["type"]["name"]
        power = self.json["power"]
        total_pp = self.json["pp"]
        accuracy = self.json["accuracy"]
        priority = self.json["priority"]
        target = self.json["target"]["name"]
        self.stats = {
            "type": move_type,
            "power": power,
            "total_pp": total_pp,
            "pp_left": total_pp,
            "accuracy": accuracy,
            "priority": priority,
            "target": target,
        }
        self.get_other_stats()

    def get_other_stats(self):
        """
        Get the other stats of the move (damage, effect, etc.)
        """
        damage_class = self.json["damage_class"]["name"]
        effect_chance = self.json["effect_chance"]
        effect_changes = self.json["effect_changes"]
        effect_entries = self.json["effect_entries"]  # [-1]["effect"]
        stat_changes = self.json["stat_changes"]
        self.other_stats = {
            "damage_class": damage_class,
            "effect_chance": effect_chance,
            "effect_changes": effect_changes,
            "effect_entries": effect_entries,
            "stat_changes": stat_changes,
        }

    def __repr__(self):
        return f"{self.name.capitalize()}"
