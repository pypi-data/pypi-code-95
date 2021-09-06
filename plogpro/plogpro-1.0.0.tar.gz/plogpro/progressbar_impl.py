from __future__   import print_function
from .progressbar import *


class ConsoleProgressBar(ProgressBar):
    """A text-based progress bar for in a terminal or console

    Arguments:
        nsteps (int)
            The number of steps that the progressbar will go through
        width (int, optional)
            The width of the progress bar
            (default: 70)
    """

    def __init__(self, nsteps, width=70):
        self.width = width
        super().__init__(nsteps)

    def draw(self):
        nblocks = round(self.progress() * self.width)
        output_string  = "|" + ('■' * nblocks).ljust(self.width) + "|"
        output_string += " {:d}/{:d}".format(self.step, self.nsteps)

        elapsed = round(self.current_time - self.start_time)
        elapsed_hours, rem = divmod(elapsed, 3600)
        elapsed_minutes, elapsed_seconds = divmod(rem, 60)
        estimated = round(elapsed / self.progress())
        estimated_hours, rem = divmod(estimated, 3600)
        estimated_minutes, estimated_seconds = divmod(rem, 60)

        output_string += " - "
        if estimated_hours > 0:
            output_string += "{:>02d}:".format(elapsed_hours)  # pragma: no cover
        if estimated_minutes > 0 or estimated_hours > 0:
            output_string += "{:02d}:".format(elapsed_minutes)  # pragma: no cover
        output_string += "{:02d}".format(elapsed_seconds)
        if estimated_minutes == 0 and estimated_hours == 0:
            output_string += "s"

        output_string += "/"
        if estimated_hours > 0:
            output_string += "{:>02d}:".format(estimated_hours)  # pragma: no cover
        if estimated_minutes > 0 or estimated_hours > 0:
            output_string += "{:02d}:".format(estimated_minutes)  # pragma: no cover
        output_string += "{:02d}".format(estimated_seconds)
        if estimated_minutes == 0 and estimated_hours == 0:
            output_string += "s"

        end = '\r' if self.step < self.nsteps else '\n'
        print(output_string, end=end, flush=True)
