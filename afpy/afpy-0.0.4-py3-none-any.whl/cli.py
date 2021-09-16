import os
from pathlib import Path


class Cli:
    def __init__(self):
        pass
    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    def cwd(self, file):
        return Path(os.path.dirname(os.path.realpath(file)))