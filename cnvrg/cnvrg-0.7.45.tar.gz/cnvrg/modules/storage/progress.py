import sys


class Progressbar:
    def __init__(self, total, bar_len=100):
        self._total = total
        self._bar_len = bar_len
        self._progress = 0

    @property
    def total(self):
        return self._total

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, progress):
        if progress > self._total:
            self._progress = self._total
        else:
            self._progress = progress

        self._print_progress()

    def _print_progress(self):
        sys.stdout.write("\r")
        prog_string = ""
        percent = self._progress / self._total
        for i in range(self._bar_len):
            prog_string += "=" if i < int(self._bar_len * percent) else " "
        sys.stdout.write("[ {} ] {}%".format(prog_string, int(percent * 100)))
        sys.stdout.flush()

    def finish(self):
        sys.stdout.write("\n")
