import pykemon_battle as pkmn


def test_pokemon():
    """
    Test the Pokemon class
    """
    weedle = pkmn.Pokemon("weedle")
    assert weedle.name == "weedle"
    assert weedle.type == ["bug", "poison"]
    assert weedle.health_points == 40
    assert weedle.stats["attack"] == 35
    assert weedle.stats["defense"] == 30
    assert weedle.stats["speed"] == 50
