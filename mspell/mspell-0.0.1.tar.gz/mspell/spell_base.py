import math
from numbers import Number
from typing import Optional

from . import utils


class SpellBase:
    _alphabet = "fcgdaeb"
    _itos = {}
    _stoi = {}

    @staticmethod
    def _get_fifth(tet: int, fifth: int) -> int:
        if fifth is None:
            tempered_fifth = utils.approximate_just_interval(3 / 2, tet)
        if math.gcd(tet, tempered_fifth) != 1:
            raise ValueError
        return tempered_fifth

    @classmethod
    def _init_missing_dicts(
        cls, letter_format: str, forward: bool, fifth: Number
    ) -> dict:
        if forward:
            base_dict = cls._itos
        else:
            base_dict = cls._stoi
        if letter_format not in base_dict:
            base_dict[letter_format] = {}
        if fifth not in base_dict[letter_format]:
            base_dict[letter_format][fifth] = {}
        return base_dict[letter_format][fifth]

    @classmethod
    def _get_spell_dict(
        cls,
        tet: int,
        letter_format: str,
        forward: bool,
        fifth: Optional[int] = None,
    ):
        # TODO move docstring to appropriate place
        fifth = cls._get_fifth(tet, fifth)
        spell_dict = cls._init_missing_dicts(letter_format, forward, fifth)
        if tet in spell_dict:
            return spell_dict[tet]

        unnormalized_dict = {}

        counter = 0

        flat_sign = "b" if letter_format == "shell" else "-"
        accidental_n = 0
        # In very small temperaments (e.g., "1-tet") c_pitch_class won't get
        # assigned within the loop below, so we initialize it here to 0.
        c_pitch_class = 0

        while True:
            if len(unnormalized_dict.items()) >= tet and (
                forward or abs(accidental_n) > 3
            ):
                break

            pitch_class = (counter * fifth) % tet

            accidental_n = math.floor((3 + counter) / len(cls._alphabet))
            accidental = utils.get_accidental(accidental_n, flat_sign=flat_sign)

            letter = cls._alphabet[(3 + counter) % len(cls._alphabet)]

            if letter + accidental == "c":
                c_pitch_class = pitch_class

            if letter_format == "shell":
                letter = letter.upper()

            if forward:
                unnormalized_dict[pitch_class] = letter + accidental
            else:
                unnormalized_dict[letter + accidental] = pitch_class

            if counter > 0:
                counter = -counter
            else:
                counter = -counter + 1

        if forward:
            out = {
                (k - c_pitch_class) % tet: v
                for k, v in unnormalized_dict.items()
            }
        else:
            out = {
                k: (v - c_pitch_class) % tet
                for k, v in unnormalized_dict.items()
            }
        spell_dict[tet] = out
        return out
