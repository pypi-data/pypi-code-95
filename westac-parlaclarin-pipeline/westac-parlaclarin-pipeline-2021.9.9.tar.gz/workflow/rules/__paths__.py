import os
import sys


def find_root(d: str) -> str:
    return os.path.join(os.getcwd().split(d)[0], d)


def fix_path():
    sys.path.insert(0, find_root("westac_parlaclarin_pipeline"))
