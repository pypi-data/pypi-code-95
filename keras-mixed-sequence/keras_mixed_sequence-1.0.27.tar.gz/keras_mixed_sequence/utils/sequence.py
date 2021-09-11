from tensorflow.keras.utils import Sequence as KerasSequence
import numpy as np


class Sequence(KerasSequence):
    """Wrapper of Keras Sequence to handle some commonly used methods and properties."""

    def __init__(
        self,
        sample_number: int,
        batch_size: int,
        elapsed_epochs: int = 0
    ):
        """Return new Sequence object.

        Parameters
        --------------
        sample_number: int,
            Length of the sequence to be split into batches.
        batch_size: int,
            Batch size for the current Sequence.
        elapsed_epochs: int = 0,
            Number of elapsed epochs to init state of generator.

        Returns
        --------------
        Return new Sequence object.
        """
        if not isinstance(sample_number, int) or sample_number == 0:
            raise ValueError(
                "Given sequence length must be a strictly positive integer."
            )

        if not isinstance(elapsed_epochs, int) or elapsed_epochs < 0:
            raise ValueError(
                "Given elapsed epochs must be a non-negative integer."
            )
        self._sample_number = sample_number
        Sequence.batch_size.fset(self, batch_size)  # pylint: disable=no-member
        self._elapsed_epochs = elapsed_epochs

    def on_epoch_end(self):
        """Handled the on epoch end callback."""
        self._elapsed_epochs += 1

    @property
    def batch_size(self) -> int:
        """Return batch size property of the sequence."""
        return self._batch_size

    @batch_size.setter
    def batch_size(self, batch_size: int) -> int:
        """Set batch size value."""
        if not isinstance(batch_size, int) or batch_size == 0:
            raise ValueError(
                "Given batch size must be a strictly positive integer."
            )
        self._batch_size = batch_size

    def reset(self):
        """Reset sequence to before training was started."""
        self._elapsed_epochs = 0

    @property
    def elapsed_epochs(self):
        """Return elapsed epochs since training started."""
        return self._elapsed_epochs

    @property
    def sample_number(self):
        """Return total number of samples in sequence."""
        return self._sample_number

    def __len__(self) -> int:
        """Return length of Sequence."""
        return int(np.ceil(self.sample_number / self.batch_size))

    @property
    def steps_per_epoch(self):
        """Number of steps to execute on the sequence."""
        return len(self)
