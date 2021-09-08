from . import PYQT4,PYQT5

if PYQT5:
    from PyQt5.QtCore import *


elif PYQT4:
    from PyQt4.QtCore import *
