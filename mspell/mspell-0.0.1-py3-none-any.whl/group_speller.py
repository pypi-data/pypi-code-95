from typing import Optional, Sequence
import numpy as np

import math

from . import utils

from .utils import get_accidental


class GroupSpeller:
    """Finds the 'best' spelling for lists of pitch-classes.

    'Best' is defined as having both
      - the shortest span on the line of fifths, and
      - the least absolute summed distance from 'D' (the central pitch of the
        white-key diatonic)

    The Pythagorean approach to spelling taken only works if the greatest common
    denominator of the (approximation to the just) fifth and the temperament
    cardinality is 1. In other words, a cycle of perfect fifths must reach every
    pitch-class. If this is not true, raises a ValueError.

    Keyword args:
        tet: sets temperament. Default: 12.

    Methods:
        __call__: takes a sequence of ints, returns an np array of strings

    Raises:
        ValueError if gcd(tet, fifth) is not 1.
    """

    def __init__(
        self,
        tet: int = 12,
        pitches: bool = False,
        letter_format: str = "shell",
    ):
        self._tet = tet
        self._pitches = pitches
        self._letter_format = letter_format
        self.fifth = utils.approximate_just_interval(3 / 2, tet)
        if math.gcd(tet, self.fifth) != 1:
            raise ValueError
        self._spelling_dict = self._build_fifth_class_spelling_dict()
        # Because of the modulo operation, it's hard to write an inverse
        # function that goes from pitch-class to fifth-class in an arbitrary
        # temperament, so instead we calculate the pitch-classes from the
        # fifth-classes and cache them:
        self._pc_to_fc_dict = {
            (i + 2) * self.fifth % self._tet: i for i in range(self._tet)
        }

    def _build_fifth_class_spelling_dict(
        self,
        bounds: tuple[int, int] = (-28, 28),
        forward: bool = True,
    ) -> dict[int, str]:
        flat_sign = "b" if self._letter_format == "shell" else "-"
        alphabet = "DAEBFCG" if self._letter_format == "shell" else "daebfcg"
        len_alphabet = 7
        out = {}
        for fc in range(bounds[0], bounds[1] + 1):
            letter = alphabet[fc % len_alphabet]
            accidental = get_accidental(
                math.floor((fc + 3) / len_alphabet), flat_sign=flat_sign
            )
            if forward:
                out[fc] = letter + accidental
            else:
                out[letter + accidental] = fc
        return out

    def __call__(self, pcs: Sequence[int]) -> list[str]:
        """
        Args:
            pcs: sequence of ints.
        """
        if len(pcs) == 0:
            return []
        unique_pcs, inv_indices = np.unique(pcs, return_inverse=True)
        fcs = np.fromiter(
            (self._pc_to_fc_dict[pc % self._tet] for pc in unique_pcs),
            dtype=unique_pcs.dtype,
        )
        indices = np.argsort(fcs)
        lower_bound = None
        span = fcs[indices[-1]] - fcs[indices[0]]
        if span > 6:
            for i, j in zip(indices, indices[1:]):
                newspan = (fcs[i] + self._tet) - fcs[j]
                if newspan < span:
                    lower_bound = fcs[j]
                    span = newspan
            if lower_bound is not None:
                fcs = np.array(
                    [fc + self._tet if fc < lower_bound else fc for fc in fcs]
                )
        fcs_sum = fcs.sum()
        while True:
            flat_fcs = fcs - self._tet
            flat_sum = abs(flat_fcs.sum())
            if flat_sum < fcs_sum:
                fcs = flat_fcs
                fcs_sum = flat_sum
            else:
                break
        spellings = [self._spelling_dict[fc] for fc in fcs]
        return list(np.array(spellings)[inv_indices])

    def pitches(
        self,
        pitches: Sequence[Optional[int]],
        rests: Optional[str] = None,
    ) -> list[str]:
        """Takes a sequence of ints, returns a list array of spelled strings.

        Args:
            pitches: sequence of ints (and possibly NoneType, if rests is
                passed).

        Keyword args:
            rests: if passed, then any items in `pitches` with the value of
                `None` will be replaced with this value.
        """

        def _kern_octave(pitch, letter):
            octave = pitch // self._tet - 5
            if octave >= 0:
                return letter * (octave + 1)
            return letter.upper() * (-octave)

        if rests is not None:
            pitches = list(pitches)
            rest_indices = [
                i for (i, pitch) in enumerate(pitches) if pitch is None
            ]
            for i in reversed(rest_indices):
                pitches.pop(i)

        pcs = self(pitches)

        # The next three lines (and the subtraction of alterations below) ensure
        # that Cb or B# (or even Dbbb, etc.) appear in the correct octave. It
        # feels a little hacky, but it works.
        sharp_sign = "#"
        flat_sign = "b" if self._letter_format == "shell" else "-"
        alterations = [
            0 + pc.count(sharp_sign) - pc.count(flat_sign) for pc in pcs
        ]

        if self._letter_format == "shell":
            out = [
                pc + str((pitch - alteration) // self._tet - 1)
                for (pitch, pc, alteration) in zip(pitches, pcs, alterations)
            ]
        else:
            out = [
                _kern_octave(pitch - alteration, pc[0]) + pc[1:]
                for (pitch, pc, alteration) in zip(pitches, pcs, alterations)
            ]
        if rests is not None:
            for i in rest_indices:
                out.insert(i, rests)
        return out
