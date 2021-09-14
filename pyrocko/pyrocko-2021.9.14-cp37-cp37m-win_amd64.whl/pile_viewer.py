
import sys
import pyrocko
if pyrocko.grumpy == 1:
    sys.stderr.write('using renamed pyrocko module: pyrocko.pile_viewer\n')
    sys.stderr.write('           -> should now use: pyrocko.gui.pile_viewer\n\n')
elif pyrocko.grumpy == 2:
    sys.stderr.write('pyrocko module has been renamed: pyrocko.pile_viewer\n')
    sys.stderr.write('              -> should now use: pyrocko.gui.pile_viewer\n\n')
    raise ImportError('Pyrocko module "pyrocko.pile_viewer" has been renamed to "pyrocko.gui.pile_viewer".')

from pyrocko.gui.pile_viewer import *
