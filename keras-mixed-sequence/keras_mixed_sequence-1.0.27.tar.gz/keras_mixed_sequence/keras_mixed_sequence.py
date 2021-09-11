"""Module offering object to deal with Mixed Keras Sequences."""
from typing import Dict, List, Tuple, Union
import numpy as np
from tqdm.auto import trange
from .utils import Sequence


class MixedSequence(Sequence):
    """Handles Mixed type input / output Sequences."""

    def __init__(
        self,
        x: Union[Dict[str, Sequence], List[Sequence], Sequence],
        y: Union[Dict[str, Sequence], List[Sequence], Sequence]
    ):
        """Create new MixedSequence object.

        Parameters
        -------------
        x: Union[Dict[str, Sequence], List[Sequence], Sequence],
            Either a Sequence, list of sequences or dictionary of Sequences.
        y: Union[Dict[str, Sequence], List[Sequence], Sequence],
            Either a Sequence, list of sequences or dictionary of Sequences.
        """
        # Store if the input / outputs are starting out as dictionaries
        self._inputs_are_dictionaries = isinstance(x, Dict)
        self._outputs_are_dictionaries = isinstance(y, Dict)

        # Casting to dictionaries if not one already
        x, y = [
            seq
            if isinstance(seq, Dict)
            else {i: sub_seq for i, sub_seq in enumerate(seq)}
            if isinstance(seq, List) else {0: seq}
            for seq in (x, y)
        ]

        any_sequence = next(iter(y.values()))

        super().__init__(
            sample_number=any_sequence.sample_number,
            batch_size=any_sequence.batch_size,
            elapsed_epochs=any_sequence.elapsed_epochs
        )

        # Checking that every value within the dictionaries
        # is now a sequence with the same length, batch size and starting epochs.
        for dictionary in (x, y):
            for _, sequence in dictionary.items():
                if self.sample_number != sequence.sample_number:
                    raise ValueError((
                        "One or more of the given Sequence length ({}) "
                        "does not match the length of other Sequences ({})."
                    ).format(
                        sequence.sample_number, self.sample_number
                    ))
                if self.batch_size != sequence.batch_size:
                    raise ValueError((
                        "One or more of the given Sequence batch size ({}) "
                        "does not match the batch size of other Sequences ({})."
                    ).format(
                        self.batch_size, sequence.batch_size
                    ))
                if self.elapsed_epochs != sequence.elapsed_epochs:
                    raise ValueError((
                        "One or more of the given Sequence elapsed_epochs ({}) "
                        "does not match the elapsed_epochs of other Sequences ({})."
                    ).format(
                        self.elapsed_epochs, sequence.elapsed_epochs
                    ))

        self._x, self._y = x, y

    def on_epoch_end(self):
        """Call on_epoch_end callback on every sub-sequence."""
        super().on_epoch_end()
        for dictionary in (self._x, self._y):
            for sequence in dictionary.values():
                sequence.on_epoch_end()

    @property
    def batch_size(self) -> int:
        """Return batch size property of the sequence."""
        return Sequence.batch_size.fget(self)  # pylint: disable=no-member

    @batch_size.setter
    def batch_size(self, batch_size: int) -> int:
        """Set batch size value to all sub sequences."""
        Sequence.batch_size.fset(self, batch_size)  # pylint: disable=no-member
        for dictionary in (self._x, self._y):
            for sequence in dictionary.values():
                sequence.batch_size = batch_size

    @property
    def features(self) -> int:
        """Return number of features."""
        return self[0][0].shape[1]

    def rasterize(self, verbose: bool = True) -> Tuple[
        Union[np.ndarray, Dict],
        Union[np.ndarray, Dict]
    ]:
        """Return rasterized sequence.

        Parameters
        -----------------------
        verbose: bool = True,
            Wether to show rendering loading bar.
        """
        return tuple([
            {
                key: np.vstack([
                    sequence[idx]
                    for idx in trange(
                        self.steps_per_epoch,
                        desc="Rendering sequence.",
                        disable=not verbose,
                        leave=False
                    )
                ])
                for key, sequence in dictionary.items()
            }
            if len(dictionary) > 1
            else np.vstack([
                sequence[idx]
                for sequence in iter(dictionary.values())
                for idx in trange(
                    self.steps_per_epoch,
                    desc="Rendering sequence.",
                    disable=not verbose,
                    leave=False
                )
            ])
            for dictionary in [
                self._x,
                self._y
            ]
        ])

    def __getitem__(self, idx: int) -> Tuple[
        Union[np.ndarray, Dict],
        Union[np.ndarray, Dict]
    ]:
        """Return batch corresponding to given index.

        Parameters
        ---------------
        idx: int,
            Index corresponding to batch to be rendered.

        Returns
        ---------------
        Return Tuple containing input and output batches.
        """
        return tuple((
            {
                key: sequence[idx]
                for key, sequence in dictionary.items()
            }
            if are_dictionaries
            else
            tuple((
                sequence[idx]
                for sequence in dictionary.values()
            ))
            if len(dictionary) > 1
            else next(iter(dictionary.values()))[idx]
            for dictionary, are_dictionaries in (
                (self._x, self._inputs_are_dictionaries),
                (self._y, self._outputs_are_dictionaries)
            )
        ))
