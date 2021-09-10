import sys

from . import __version__
from .pyapibp import pyapibp

def main():
    try:
        pyapibp()
    except:
        sys.exit(0)

if __name__ == "__main__":
    main()
