from abc  import ABCMeta, abstractmethod
from time import time


class ProgressBar(metaclass=ABCMeta):
    """Base class that provides an interface for progress bars

    To create a progress bar, create an instance of one of its implementations.
    The progressbar can then be updated by calling the method ``update()``.

    To implement a new progress bar, create a class that derives from
    ``ProgressBar`` and implement the method ``draw()``. This method should draw
    the progress bar based on the accessible member variables. If you need to do
    anything once in the beginning or the and, you can override the ``setup()``
    and/or ``teardown()`` methods respectively.

    Warning:
        The ``update()`` method should **not** be overwritten.

    Arguments:
        nsteps (int)
            The number of steps that the progressbar will go through

    Attributes:
        nsteps (int)
            The number of steps that the progressbar will go through
        step (int)
            The current step of the iteration, going from ``0`` to ``nsteps``
        start_time (float)
            The start time of the progress bar in seconds since Epoch
        current_time (float)
            The current time of the progress bar in seconds since Epoch
    """

    def __init__(self, nsteps):
        self.nsteps = nsteps
        self.step = 0
        self.start_time = time()
        self.current_time = time()
        self.setup()

    def __del__(self):
        self.teardown()

    def setup(self):
        pass

    def teardown(self):
        pass

    def update(self, step=None):
        """Update the progressbar

        Arguments:
            step (int, optional)
                The current step of the operation, the progress will be
                increased with one step if not provided
                (default: `None`)
        """
        self.current_time = time()
        if step is None:
            self.step += 1
        else:
            self.step = step
        self.draw()

    def progress(self):
        """Get the progress as a number between 0 and 1

        Returns:
            float: The progress
        """
        return self.step / self.nsteps

    @abstractmethod
    def draw(self):
        raise NotImplementedError
