import os

class Cli:
    def __init__(self):
        pass
    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')