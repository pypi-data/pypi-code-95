
import sys
import pyrocko
if pyrocko.grumpy == 1:
    sys.stderr.write('using renamed pyrocko module: pyrocko.marker\n')
    sys.stderr.write('           -> should now use: pyrocko.gui.marker\n\n')
elif pyrocko.grumpy == 2:
    sys.stderr.write('pyrocko module has been renamed: pyrocko.marker\n')
    sys.stderr.write('              -> should now use: pyrocko.gui.marker\n\n')
    raise ImportError('Pyrocko module "pyrocko.marker" has been renamed to "pyrocko.gui.marker".')

from pyrocko.gui.marker import *
