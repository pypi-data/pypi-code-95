import os
import inspect


def get_names():
    current_directory = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    with open((f'{current_directory}/names.txt')) as f:
        names = set([n[:-1] for n in f.readlines()])
        return names
