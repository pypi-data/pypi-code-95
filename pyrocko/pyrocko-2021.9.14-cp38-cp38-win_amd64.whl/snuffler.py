
import sys
import pyrocko
if pyrocko.grumpy == 1:
    sys.stderr.write('using renamed pyrocko module: pyrocko.snuffler\n')
    sys.stderr.write('           -> should now use: pyrocko.gui.snuffler\n\n')
elif pyrocko.grumpy == 2:
    sys.stderr.write('pyrocko module has been renamed: pyrocko.snuffler\n')
    sys.stderr.write('              -> should now use: pyrocko.gui.snuffler\n\n')
    raise ImportError('Pyrocko module "pyrocko.snuffler" has been renamed to "pyrocko.gui.snuffler".')

from pyrocko.gui.snuffler import *
