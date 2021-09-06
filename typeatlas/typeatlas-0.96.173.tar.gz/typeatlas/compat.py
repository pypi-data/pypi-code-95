# -*- coding: utf-8 -*-
#
#    TypeAtlas Qt Compatibility
#    Written in 2018-2021 by Milko Krachounov
#
#    This file is part of TypeAtlas.
#
#    To the extent possible under law, Milko Krachunov has waived all copyright
#    and related or neighboring rights to TypeAtlas Qt Compatibility.
#    This software is distributed without any warranty.
#
#    You should have received a copy of the CC0 legalcode along with this
#    work.  If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.
#

# License note:
#
# This module will load Qt and PyQt or PySide and import their utilities.
# At the time of writing Qt and PySide were licensed under the GNU LGPL,
# and PyQt was under the GNU GPL.

"""Support Qt 4, 5, possibly 6 when someone gives it to me, with PySide
and PyQt5, whichever sucks less.

The Qt modules from the respective PyQt5/PySide2 package are imported
in the module's namespace.

TODO: Use __getattr__ when we drop pre-Python 3.7 if this even works
with our code.
"""


import sys
import os
import os.path
from operator import methodcaller
from typeatlas import proginfo
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

DEFAULT_ORDER = [
    'PyQt5',    # Qt 5 sucks at font rendering
    'PySide2',  # Maybe this will not crash
    'PyQt4',    # Crashes? (TODO: find why it segfaults)
    'PySide',   # PySide doesn't have QRawFont, segfaults
]

QT_PYSIDE_VERSION = {4: 'PySide', 5: 'PySide2'}


configuredStyle = None


def _get_qt(order=DEFAULT_ORDER):
    global configuredStyle
    
    exc = None

    order = list(order)

    for name in order:
        if name in sys.modules:
            order = [name]
            break

    filename = os.path.join(proginfo.CONFIG_DIR, proginfo.MAIN_CONFIG)
    if os.path.exists(filename):
        parser = configparser.RawConfigParser()
        parser.read_file(open(filename))
        if parser.has_option('Runtime', 'qt_version'):
            ver = parser.get('Runtime', 'qt_version')
            if ver.isdigit() and ver.isascii():
                preferred = {'PyQt' + ver, QT_PYSIDE_VERSION.get(int(ver))}
                order.sort(key=lambda v: v not in preferred)

        if parser.has_option('Runtime', 'qt_bindings'):
            bindings = parser.get('Runtime', 'qt_bindings')
            if bindings == 'pyqt':
                order.sort(key=lambda v: not v.startswith('PyQt'))
            elif bindings == 'pyside':
                order.sort(key=lambda v: not v.startswith('PySide'))

        if parser.has_option('Runtime', 'qt_style'):
            configuredStyle = parser.get('Runtime', 'qt_style')

    for name in order:
        try:
            if name == 'PyQt5':
                from PyQt5 import QtCore, QtNetwork, QtGui, QtWidgets
                try:
                    from PyQt5 import QtSvg
                except ImportError:
                    QtSvg = None

                return (QtCore, QtNetwork, QtGui, QtWidgets, QtCore, QtSvg,
                        QtCore.pyqtSlot, QtCore.pyqtSignal, 5, False)
            elif name == 'PySide2':
                from PySide2 import QtCore, QtNetwork, QtGui, QtWidgets
                try:
                    from PySide2 import QtSvg
                except ImportError:
                    QtSvg = None

                return (QtCore, QtNetwork, QtGui, QtWidgets, QtCore, QtSvg,
                        QtCore.Slot, QtCore.Signal, 5, True)
            elif name == 'PySide':
                from PySide import QtCore, QtNetwork, QtGui
                try:
                    from PySide import QtSvg
                except ImportError:
                    QtSvg = None

                return (QtCore, QtNetwork, QtGui, QtGui, QtGui, QtSvg,
                        QtCore.Slot, QtCore.Signal, 4, True)
            elif name == 'PyQt4':
                from PyQt4 import QtCore, QtNetwork, QtGui, QtCore
                try:
                    from PyQt4 import QtSvg
                except ImportError:
                    QtSvg = None

                return (QtCore, QtNetwork, QtGui, QtGui, QtGui, QtSvg,
                        QtCore.pyqtSlot,  QtCore.pyqtSignal, 4, False)

        except ImportError as exc:
            print("%s failed to load: %s: %s" % (name,
                                                 type(exc).__name__, exc),
                  file=sys.stderr)

    raise exc
             

(QtCore, QtNetwork, QtGui, QtWidgets, QtModelProxies, QtSvg,
 Slot, Signal, QT_VERSION, usesPySide) = _get_qt()

usesPyQt = not usesPySide
QT_BINDINGS = 'PyQt' if usesPyQt else 'PySide'

Qt = QtCore.Qt

if QtSvg is None:
    del QtSvg


if QT_VERSION == 4:
    def setResizeMode(header, mode):
        return header.setResizeMode(mode)

else:
    def setResizeMode(header, mode):
        return header.setSectionResizeMode(mode)


if usesPySide and QT_VERSION >= 5:
    # Support for bytes in PySide2 is shiboken
    qtGetBytes = methodcaller('data')
else:
    qtGetBytes = bytes


if usesPySide:
    try:
        if QT_VERSION >= 5:
            import shiboken2 as shiboken
        else:
            import shiboken
    except ImportError:
        shiboken = None

    def unwrap(ob):
        return int(shiboken.getCppPointer(ob)[0])


else:
    import sip

    def unwrap(ob):
        return int(sip.unwrapinstance(ob))
