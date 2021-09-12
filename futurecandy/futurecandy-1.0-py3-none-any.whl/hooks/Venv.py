"""Python script for venv.hook.futurecandy."""

from os import system, path
from sys import argv

system("python -m venv " + path.join(argv[1], ".venv"))
