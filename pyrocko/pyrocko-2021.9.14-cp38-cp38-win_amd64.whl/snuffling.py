
import sys
import pyrocko
if pyrocko.grumpy == 1:
    sys.stderr.write('using renamed pyrocko module: pyrocko.snuffling\n')
    sys.stderr.write('           -> should now use: pyrocko.gui.snuffling\n\n')
elif pyrocko.grumpy == 2:
    sys.stderr.write('pyrocko module has been renamed: pyrocko.snuffling\n')
    sys.stderr.write('              -> should now use: pyrocko.gui.snuffling\n\n')
    raise ImportError('Pyrocko module "pyrocko.snuffling" has been renamed to "pyrocko.gui.snuffling".')

from pyrocko.gui.snuffling import *
