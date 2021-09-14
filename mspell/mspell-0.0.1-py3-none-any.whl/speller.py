from typing import Optional, Sequence, Union

import numpy as np


from .spell_base import SpellBase
from . import utils


ALPHABET = "fcgdaeb"


class Speller(SpellBase):
    """Spells pitches or pitch-classes in specified temperament.

    When spelling pitches, C4 is always 5 * c, where c is the cardinality of the
    temperament. So in 12-tet, C4 = 60; in 31-tet, C4 = 155, and so on.

    Double-sharps and flats (and beyond) are always indicated by repetition of
    the accidental symbol (e.g., F##).

    Keyword args:
        tet: integer. Default 12.
        pitches: boolean. If true, spells pitches by default (e.g., in 12-tet,
            60 = "C4"; note the octave number). If false, spells pitch-classes
            by default (e.g., in 12-tet, 60 = "C").
            Default: False.
        rests: boolean. If true, spells None as "Rest". If false, raises a
            TypeError on None values.
        letter_format: string.
            Possible values:
                "shell": e.g., "C4", "Ab2", "F#7"
                "kern": e.g., "c", "DD", "b-", "F#"

    Raises:
        ValueError: if letter_format is not "shell" or "kern".
        ValueError: if gcd(tet, utils.approximate_just_interval(3/2, tet))
            is not 1.

    Methods:
         __call__(item, pitches=None)
    """

    def __init__(
        self,
        tet: int = 12,
        pitches: bool = False,
        rests: bool = True,
        letter_format: str = "shell",
    ):
        self._tet = tet
        self._pitches = pitches
        self._rests = rests
        if letter_format == "shell":
            self._pitch = self._shell_pitch
        elif letter_format == "kern":
            self._pitch = self._kern_pitch
        else:
            raise ValueError(
                f"letter_format {letter_format} not in ('shell', 'kern')"
            )
        self._spelling_dict = self._get_spell_dict(
            tet, letter_format, forward=True
        )

    def _shell_pitch(self, pc_string: str, pitch_num: int) -> str:
        """Appends an octave number to a pitch-class (e.g., "C#" becomes "C#3")"""
        octave = pitch_num // self._tet - 1
        return pc_string + str(octave)

    def _kern_pitch(self, pc_string: str, pitch_num: int) -> str:
        if pc_string[0] == "c" and pc_string[-1] == "-":
            pitch_num += self._tet
        temp_num = (pitch_num % self._tet) + (self._tet * 5)

        if temp_num > pitch_num:
            pc_string = pc_string[0].upper() + pc_string[1:]
            temp_num -= self._tet
        while temp_num > pitch_num:
            pc_string = pc_string[0] + pc_string
            temp_num -= self._tet
        while temp_num < pitch_num:
            pc_string = pc_string[0] + pc_string
            temp_num += self._tet

        return pc_string

    @utils.nested_method
    def __call__(
        self, item: Union[int, Sequence], pitches: Optional[bool] = None
    ) -> Union[str, Sequence[str]]:
        """Spells integers as musical pitches or pitch-classes.

        Args:
            item: either an integer, or an (arbitrarily deep and nested)
                list-like of integers (and None values, if Speller was
                initialized with rests=True).

        Keyword args:
            pitches: boolean. Overrides the default setting for
                the Speller instance. If true, spells pitches (e.g., in 12-tet,
                60 = "C4"). If false, spells pitch-classes (e.g., in 12-tet,
                60 = "C").
                Default: None.

        Returns:
            A string representing a single pitch, if item is an integer.
            A list of strings, if item is a list-like, with the same depth and
                nesting as item.

        Raises:
            TypeError if iter() fails on item and item is not an integer (or
                None, if Speller was initialized with rests=True.)
        """
        if pitches is None:
            pitches = self._pitches

        if not isinstance(item, (int, np.integer)):
            if item is not None and self._rests:
                raise TypeError(
                    "Speller.spelled_list() can only take iterables of "
                    "integers, or None for rests"
                )
            else:
                raise TypeError(
                    "Speller.spelled_list() with rests=False can only take "
                    "iterables of integers"
                )

        if item is None:
            return "Rest"

        if item < 0:
            return item

        pitch_class = self._spelling_dict[item % self._tet]
        if not pitches:
            return pitch_class

        return self._pitch(pitch_class, item)
