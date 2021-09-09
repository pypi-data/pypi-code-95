import sys
import os
import re
from pathlib import Path, PurePath
import obsinfo

def main():
    file = Path(obsinfo.__file__).parent.joinpath("version.py")
    
    version={}
    with open(file) as fp:
        exec(fp.read(),version)
    
    name="obsinfo"
    version=version['__version__']
    
    print(name + " v" + version)
