"""Module offering object to handle Vector Keras Sequences."""
import numpy as np
from .sequence import Sequence


class VectorSequence(Sequence):
    """Wrapper of Keras Sequence to handle some commonly used methods and properties."""

    def __init__(
        self,
        vector: np.ndarray,
        batch_size: int,
        random_state: int = 42,
        elapsed_epochs: int = 0,
        shuffle: bool = True
    ):
        """Return new Sequence object.

        Parameters
        -------------------------------------
        vector: np.ndarray,
            Numpy array with data to be split into batches.
        batch_size: int,
            Batch size for the current Sequence.
        random_state: int = 42,
            Random random_state to use for reproducibility.
        elapsed_epochs: int = 0,
            Number of elapsed epochs to init state of generator.
        shuffle: bool = True,
            Wethever to shuffle or not the sequence.

        Returns
        -------------------------------------
        Return new Sequence object.
        """
        super().__init__(
            len(vector),
            batch_size,
            elapsed_epochs
        )
        self._random_state = random_state
        self._vector = vector
        self._shuffle = shuffle
        self._shuffled = self._shuffle_vector()

    def _shuffle_vector(self):
        """Shuffle data."""
        if not self._shuffle:
            return self._vector
        state = np.random.RandomState(  # pylint: disable=no-member
            seed=self._random_state + self._elapsed_epochs
        )
        indices = np.arange(self.sample_number)
        state.shuffle(indices)
        return self._vector[indices]

    def on_epoch_end(self):
        """Shuffle private numpy array on every epoch end."""
        super().on_epoch_end()
        self._shuffled = self._shuffle_vector()

    @property
    def features(self) -> int:
        """Return number of features."""
        return self[0][0].shape[1]

    def __getitem__(self, idx: int) -> np.ndarray:
        """Return batch corresponding to given index.

        Parameters
        ---------------------
        idx: int,
            Index corresponding to batch to be rendered.

        Raises
        ---------------------
        ValueError,
            If given batch index is greater than amount of batches.

        Returns
        ---------------------
        Return numpy array corresponding to given batch index.
        """
        if idx >= self.steps_per_epoch:
            raise ValueError(
                (
                    "Given index {idx} is greater than the number "
                    "of steps per epoch of this sequence {steps}."
                ).format(
                    idx=idx,
                    steps=self.steps_per_epoch
                )
            )
        return self._shuffled[idx * self.batch_size: (idx + 1) * self.batch_size]
