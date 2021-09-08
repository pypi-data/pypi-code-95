import sys
import importlib


qts = ['PyQt5', 'PyQt4']  ## ordered by preference

# check if PyQt alredy imported
QT_LIB = None

for lib in qts:
    if lib in sys.modules:
        QT_LIB = lib
        break

# if not imported let's try to import any
if QT_LIB is None:
    for lib in qts:
        try:
            importlib.import_module(lib)
            QT_LIB = lib
            break
        except ImportError:
            pass
if QT_LIB is None:
    ImportError("PyQt not found")

# now some PyQt is imported
PYQT5 = False
PYQT4 = False

if QT_LIB == 'PyQt5':
    PYQT5 = True

elif QT_LIB == 'PyQt4':
    PYQT4 = True

