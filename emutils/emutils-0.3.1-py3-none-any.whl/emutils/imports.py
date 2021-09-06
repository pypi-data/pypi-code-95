"""
This module contains a list of common imports
Useful to rapidly start a Notebook without writing all imports manually.

It will also set up the main logging.Logger

## Usage

```python
from emutils.imports import *
```

## Imports
- Python Standard Modules: os, sys, time, platform, gc, math, random, collections, itertools, re, urllib, importlib, warnings, logging
- Several common function/class from Pyton Standard Library
- Several common function from emutils
- Utilities: tqdm
- Machine Learning: xgboost, sklearn
- Data Science: numpy, pandas, networkx
- Plotting: matplotlib, seaborn, plotly, graphviz

"""

# Python 3 stuff
import os
import sys
import time
import platform
import gc
import math
import random
import pickle
import collections
import itertools
import functools
import re
import logging
import urllib
import importlib
import warnings

from itertools import product, combinations, permutations, combinations_with_replacement, chain
from math import floor, ceil, isnan, isinf, log, log10, exp, sqrt
from collections import defaultdict, Counter
from enum import Enum
from functools import partial
from typing import List, Dict, Union, Iterable
from argparse import ArgumentParser

from .utils import in_ipynb, prod, copy_plotlyjs, import_tqdm
from .utils import BaseAttrDict
from .utils import display

print('Python ', platform.python_version())
print('Python Executable:', sys.executable)

print("CWD = ", os.getcwd())


# Logging
def __setup_logging(logging_format='[%(asctime)s] %(levelname)s:\t %(message)s', time_format="%Y-%m-%d %H:%M:%S"):
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(logging_format, time_format))
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.INFO)


__setup_logging()

# Utilities
try:
    # Import iPy or command-line TQDM
    tqdm = import_tqdm()
    # Common typo
    tqmd = tqdm
except:
    pass

# DataScience Basics
try:
    import numpy
    np = numpy
    print('NumPy', np.__version__, end="")

    try:
        import pandas
        pd = pandas
        print(' | Pandas', pd.__version__, end="")
    except:
        pass

    try:
        import scipy
        sp = scipy
        import scipy.stats as stats
        print(' | SciPy', sp.__version__, end="")
    except:
        pass

    try:
        import networkx
        nx = networkx
        print(' | NetworkX', nx.__version__, end="")
    except:
        pass

except:
    pass
# DataScience Basics End

print()

# Machine Learning
try:
    import sklearn
    print('scikit-learn', sklearn.__version__, end=" | ")
except:
    pass

try:
    import xgboost
    xgb = xgboost
    print('xgboost', xgb.__version__, end=" | ")
except:
    pass

print("\b\b")

# Visualization
# try:
import matplotlib

mpl = matplotlib
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.patches as mpatches

print('MatPlotLib', mpl.__version__, end=" | ")
try:
    import seaborn
    sns = seaborn
    print('Seaborn', sns.__version__, end=" | ")
except:
    pass
# except:
#     pass

try:
    import graphviz
    print('GraphViz', graphviz.__version__, end=" | ")
except:
    pass

try:
    import plotly.offline as pyo
    if in_ipynb():
        pyo.init_notebook_mode(connected=True)
    import plotly
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots

    print('Plotly', plotly.__version__, end=f" (mode = {'notebook' if in_ipynb() else 'script'})")
    copy_plotlyjs('.')

except:
    pass

print("\n")
