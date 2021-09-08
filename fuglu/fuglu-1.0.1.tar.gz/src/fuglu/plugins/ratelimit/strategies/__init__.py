# -*- coding: UTF-8 -*-
from os.path import dirname, basename, isfile
from collections import defaultdict
import glob
modules = glob.glob(dirname(__file__)+"/*.py")

# export all module names in this package
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]

AVAILABLE_STRATEGIES = []
AVAILABLE_BACKENDS = defaultdict(dict)

# export aggregated list of strategies and backends
# defined by all modules in this package
for m in __all__:
    module = __import__(m, globals(), locals(), [], 1)
    try:
        AVAILABLE_STRATEGIES.append(module.STRATEGY)
        AVAILABLE_BACKENDS.update(module.BACKENDS)
    except AttributeError:
        # not all modules necessarily contain a strategy implementation,
        # for example backendint which contains the abstract base class
        # for the backends
        pass

__all__.append('AVAILABLE_STRATEGIES')
__all__.append('AVAILABLE_BACKENDS')
