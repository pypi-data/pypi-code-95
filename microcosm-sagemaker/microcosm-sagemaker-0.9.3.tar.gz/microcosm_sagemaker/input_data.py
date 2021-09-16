
import contextlib
import os
from pathlib import Path
from typing import Union


class InputData:
    def __init__(self, path: Union[str, Path]):
        self.path = Path(path)

    def __repr__(self) -> str:
        return f'{type(self).__name__}("{str(self.path)}")'

    @contextlib.contextmanager
    def cd(self):
        """
        Change working directory to directory of input data.

        """
        old_path = os.getcwd()
        os.chdir(self.path)
        try:
            yield
        finally:
            os.chdir(old_path)
