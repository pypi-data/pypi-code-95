"""Module to deliver global variables."""
from .manager import Manager

def initialize():
    global manager
    manager = Manager()