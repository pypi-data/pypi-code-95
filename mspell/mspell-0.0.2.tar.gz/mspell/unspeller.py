from .spell_base import SpellBase
from . import utils


class Unspeller(SpellBase):
    """Takes spelled pitches or pitch-classes and returns pitch numbers.

    When spelling pitches, C4 is always 5 * c, where c is the cardinality of
    the temperament. So in 12-tet, C4 = 60; in 31-tet, C4 = 155, and so on.

    Expects double-sharps and flats (and beyond) to be indicated by repetition
    of the accidental symbol (e.g., F##).

    Keyword args:
        tet: integer. Default 12.
        pitches: boolean. If true, expects pitches (e.g., in 12-tet, "C4" = 60).
            If false, expects pitch-classes (e.g., in 12-tet, "C" = 0).
            Default: False.
        letter_format: string.
            Possible values:
                "shell": e.g., "C4", "Ab2", "F#7"
                "kern": e.g., "c", "DD", "b-", "F#"

    Raises:
        ValueError: if letter_format is not "shell" or "kern".
        ValueError: if gcd(tet, utils.approximate_just_interval(3/2, tet))
            is not 1.

    Methods:
    # QUESTION where and how to document __call__()?
        unspelled(item, pitches=None)
    """

    def __init__(self, tet=12, pitches=False, letter_format="shell"):
        self._tet = tet
        self._pitches = pitches
        if letter_format not in ("shell", "kern"):
            raise ValueError(
                f"letter_format {letter_format} not in ('shell', 'kern')"
            )
        self._pc_dict = self._get_spell_dict(tet, letter_format, forward=False)
        # self._pc_dict = spell.speller.build_spelling_dict(
        #     tet, forward=False, letter_format=letter_format)
        if letter_format == "shell":
            self._unspell = self._unspell_shell
        elif letter_format == "kern":
            self._unspell = self._unspell_kern

    def _unspell_shell(self, item, pitches):
        i = 0
        try:
            while not item[i].isdigit() and not item[i] == "-":
                i += 1
        except IndexError:
            if pitches:
                raise ValueError(f"{item} is not a pitch")
        pc = self._pc_dict[item[:i]]
        if not pitches:
            return pc
        return (int(item[i:]) + 1) * self._tet + pc

    def _unspell_kern(self, item, pitches):
        letter = item[0]
        if letter.isupper():
            octave = 4
            increment = -1
        else:
            octave = 5
            increment = 1
        i = 1
        while i < len(item) and item[i] == letter:
            octave += increment
            i += 1
        pc_string = item[i - 1 :].lower()
        pc = self._pc_dict[pc_string]
        if not pitches:
            return pc
        if pc_string.startswith("c-"):
            octave -= 1
        return octave * self._tet + pc

    def __call__(self, item, pitches=None):
        return self.unspelled(item, pitches=pitches)

    @utils.nested_method
    def unspelled(self, item, pitches=None):
        """Takes spelled pitch strings, returns integers.

        Args:
            item: either a pitch-string, or an (arbitrarily deep and nested)
                list-like of pitch-strings.

        Keyword args:
            pitches: boolean. Temporarily overrides the current setting for
                the Speller instance. If true, expects pitches (e.g., in 12-tet,
                "C4" = 60). If false, expects pitch-classes (e.g., in 12-tet,
                "C" = 0).
                Default: None.

        Returns:
            An integer, if item is a string.
            A list of integers, if item is a list-like, with the same depth and
                nesting as item.
        """
        if pitches is None:
            pitches = self._pitches

        # MAYBE implement rests?
        # if item == "Rest" and rests:
        #     return None

        return self._unspell(item, pitches=pitches)


if __name__ == "__main__":
    usp = Unspeller(pitches=True)
    # print(usp(["C4", "C5", ["Eb5", "F#4"]], pitches=True, letter_format="kern"))
    print(usp(["C4"]))
    breakpoint()
