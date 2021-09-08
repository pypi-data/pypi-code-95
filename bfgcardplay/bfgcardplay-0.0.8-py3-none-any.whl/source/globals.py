"""Module to deliver global variables."""
from .manager import Manager

def initialize_manager():
    global manager
    manager = Manager()
    return manager