from magic.shared.display import Color, in_color
from magic.shared.spellbook import read_spell


def show_spell(magic_word, spell_args, skip_arguments_provided=False):
    spell = read_spell(magic_word)
    color = Color.CYAN

    if not spell:
        raise Exception(f"Spell not found for magic word '{magic_word}'")

    print(f'{in_color("Description:", color)} {spell["description"]}')
    print(f'{in_color("Magic words:", color)} {", ".join(spell["magicWords"])}')
    print(in_color("Commands:", color))
    for command in spell["commands"]:
        print(f"  {command}")

    argument_count = spell.get("argumentCount")
    if argument_count is None:
        print(f'{in_color("Arguments required:", color)} None')
    else:
        print(f'{in_color("Arguments required:", color)} {argument_count}')

    if skip_arguments_provided:
        return

    print(f'{in_color("Arguments provided:", color)} {len(spell_args)}')
    for idx, arg in enumerate(spell_args):
        print(f"  $a{idx}: {arg}")
