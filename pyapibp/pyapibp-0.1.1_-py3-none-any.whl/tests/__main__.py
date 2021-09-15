import os, sys, inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from pyapibp import pyapibp

try:
    apb = pyapibp(test_mode=True)
except:
    sys.exit(0)
