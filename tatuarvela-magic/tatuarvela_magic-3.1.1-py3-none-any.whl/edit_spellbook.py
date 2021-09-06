import subprocess  # nosec

from magic.shared.config import SPELLBOOK_EDITOR, SPELLBOOK_PATH
from magic.shared.display import Color, in_color


def edit_spellbook():
    print(f"Opening spellbook in {in_color(SPELLBOOK_EDITOR, Color.CYAN)}...")
    subprocess.call([SPELLBOOK_EDITOR, SPELLBOOK_PATH])  # nosec
