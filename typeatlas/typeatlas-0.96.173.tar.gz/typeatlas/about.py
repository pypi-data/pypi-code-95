# -*- coding: utf-8 -*-
#
#    TypeAtlas About Dialogs
#    Copyright (C) 2018-2021 Milko Krachounov
#
#    This file is part of TypeAtlas
#
#    TypeAtlas is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    TypeAtlas is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with TypeAtlas.  If not, see <http://www.gnu.org/licenses/>.
#

"""The about dialogs, acknowledging everyone providing fonts on
your system."""

import typeatlas.proginfo as proginfo
import typeatlas.osinfo as osinfo
from typeatlas.compat import QtCore, QtGui, QtWidgets, Qt, Slot
from typeatlas.uitools import getIcon, getImage, Toolbox, iconSize
from typeatlas.uitools import generalSize, generalWidth, generalHeight
from typeatlas.langutil import _, N_

import os
import platform
from collections.abc import Iterator


def w(refWidth: int) -> int:
    """Get widgth"""
    return generalWidth(refSize=refWidth)

def h(refHeight: int) -> int:
    """Get height"""
    return generalHeight(refSize=refHeight)


px = w
py = h


class TypeAtlasAbout(QtWidgets.QDialog):

    def __init__(self, parent: QtWidgets.QWidget=None):
        super(TypeAtlasAbout, self).__init__(parent)
        self.setWindowTitle(_("About %s") % (_(proginfo.PROGRAM_NAME), ))

        self.image = QtWidgets.QLabel(self)
        pixmap = getImage('splash').pixmap(w(640), h(640))
        self.image.setPixmap(pixmap)
        self.resize(pixmap.size())

        text = [_(proginfo.PROGRAM_NAME) + ' ' + proginfo.VERSION_HUMAN_SHORT]


        self.text = QtWidgets.QLabel(self)
        self.text.setTextFormat(Qt.PlainText)
        self.text.setText('\n'.join(text))
        self.text.move(px(10), py(170))

        self.buttons = buttons = QtWidgets.QDialogButtonBox(self)
        buttons.addButton(buttons.Ok)
        buttons.accepted.connect(self.accept)

        self.buttons.move(px(12), py(330))


class FreeTypeAbout(QtWidgets.QDialog):

    def __init__(self, parent: QtWidgets.QWidget=None, version: str=None):
        super(FreeTypeAbout, self).__init__(parent)
        self.setWindowTitle(_("About FreeType"))

        if version is None:
            version = osinfo.freetype_version()

        self.image = QtWidgets.QLabel(self)
        self.image.setPixmap(getImage('freetype-logo', '.png').pixmap(584, 338))
        self.resize(w(584), h(338))

        self.text = QtWidgets.QLabel(self)
        self.text.setTextFormat(Qt.PlainText)
        text = [_("Fonts rendering provided by FreeType %s") % (version, ),
                "",
                _("FreeType is a cross-platform multi-format library "
                  "for font rasterization.")]

        self.text.setText('\n'.join(text))
        self.text.move(px(12), py(220))

        self.buttons = buttons = QtWidgets.QDialogButtonBox(self)
        buttons.addButton(buttons.Ok)
        buttons.accepted.connect(self.accept)

        self.buttons.move(px(12), py(300))


class FontConfigAbout(QtWidgets.QDialog):

    def __init__(self, parent: QtWidgets.QWidget=None, version: str=None):
        super(FontConfigAbout, self).__init__(parent)
        self.setWindowTitle(_("About fontconfig"))

        if version is None:
            from typeatlas import fontlist
            version = fontlist.FontFinder().fontconfig_version()

        self.image = QtWidgets.QLabel(self)
        self.image.setPixmap(getImage('freedesktop-logo').pixmap(586, 91))
        self.resize(w(596), h(240))

        self.text = QtWidgets.QLabel(self)
        self.text.setTextFormat(Qt.PlainText)
        text = [_("TypeAtlas is powered by the font database of fontconfig %s")
                                    % (version, ),
                "",
                _("fontconfig is freedesktop.org's library for font "
                  "discovery, substitution and configuration.")]

        self.text.setText('\n'.join(text))
        self.text.move(px(12), py(120))

        self.buttons = buttons = QtWidgets.QDialogButtonBox(self)
        buttons.addButton(buttons.Ok)
        buttons.accepted.connect(self.accept)

        self.buttons.move(px(12), py(190))



class PythonAbout(QtWidgets.QDialog):

    def __init__(self, parent: QtWidgets.QWidget=None):
        super(PythonAbout, self).__init__(parent)
        self.setWindowTitle(_("About Pythonⓡ"))

        layout = QtWidgets.QVBoxLayout()

        self.icon = QtWidgets.QLabel()
        self.icon.setPixmap(getImage('python-powered-w').pixmap(generalSize(refSize=256)))
        text = [
                _('This program is powered by <b>Python®</b> %s')
                            % (platform.python_version(), ),
                "",
                _("Python is a cross-platform high-level programming language"),
                "",
                _("Currently using %s implementation")
                            % (platform.python_implementation(), ),
                "",
        ]

        if platform.python_implementation() == 'CPython':
            text.extend([
                _('The Python language is distributed under the terms of the '
                  '<a href="%s">PSF License Agreement.</a>')  % (
                            ('https://docs.python.org/3/license.html', )),

            ])

        text.extend([
                _('“Python” and the Python logos are trademarks or registered '
                  'trademarks of the Python Software Foundation, used in '
                  'TypeAtlas under <a href="%s">PSF Trademark Usage Policy</a> '
                  'as published by the Foundation.') % (
                            ('https://www.python.org/psf/trademarks/', )),
        ])

        self.text = QtWidgets.QLabel()
        self.text.setTextFormat(Qt.RichText)
        self.text.setWordWrap(True)
        self.text.setText('<br>\n'.join(text))

        self.buttons = buttons = QtWidgets.QDialogButtonBox()
        buttons.addButton(buttons.Ok)
        buttons.accepted.connect(self.accept)

        layout.addWidget(self.icon)
        layout.addWidget(self.text)
        layout.addWidget(self.buttons)
        layout.setAlignment(Qt.AlignHCenter)

        self.setLayout(layout)


class SystemAbout(QtWidgets.QDialog):

    def __init__(self, parent: QtWidgets.QWidget=None):
        super(SystemAbout, self).__init__(parent)
        self.setWindowTitle(_("About operating system"))

        layout = QtWidgets.QHBoxLayout()

        self.icon = QtWidgets.QLabel()
        if osinfo.oslogo.icon:
            pixmap = getIcon(osinfo.oslogo.icon).pixmap(iconSize(refSize=64))
            self.icon.setPixmap(pixmap)
        elif osinfo.oslogo.symbol:
            self.icon.setText(osinfo.oslogo.symbol)
            if osinfo.oslogo.font:
                self.font = QtGui.QFont(osinfo.oslogo.font)
                self.font.setPointSize(48)
                self.icon.setFont(self.font)

        text = [platform.node()]
        text.append(' '.join(platform.system_alias(platform.system(),
                                                   platform.release(),
                                                   platform.version())))
        distname, version, distid = platform.dist()
        if distname:
            text.append(' '.join([distname.capitalize(), version, distid]))

        text.append(_('System: %s') % (platform.machine(), ))

        self.text = QtWidgets.QLabel()
        self.text.setTextFormat(Qt.PlainText)
        self.text.setText('\n'.join(text))

        self.buttons = buttons = QtWidgets.QDialogButtonBox()
        buttons.addButton(buttons.Ok)
        buttons.accepted.connect(self.accept)

        layout.addWidget(self.icon)
        layout.addWidget(self.text)
        layout.addWidget(self.buttons)

        self.setLayout(layout)


class AboutDialogs(Toolbox):

    def __init__(self, mainWindow: QtWidgets.QWidget, *args, **kwargs):
        self.mainWindow = mainWindow
        self.freeTypeVersion = osinfo.freetype_version()
        self.fontConfigVersion = mainWindow.finder.fontconfig_version()
        super(AboutDialogs, self).__init__(*args, **kwargs)

    @property
    def actionParent(self) -> QtCore.QObject:
        return self.mainWindow

    def actionDefinitions(self) -> Iterator:
        if self.freeTypeVersion:
            yield self.aboutFreeType, _("About FreeType"),
        if self.fontConfigVersion:
            yield self.aboutFontConfig, _("About fontconfig")

        yield self.action(self.aboutQt, _("About Qt®"), icon='qtlogo')
        yield self.action(self.aboutPython, _("About Python®"),
                          icon='applications-python')
        yield self.action(self.aboutSystem, _("About operating system"),
                          icon='distributor-logo')
        yield self.separator()
        yield self.action(self.about,
                          _("About %s") % (_(proginfo.PROGRAM_NAME), ),
                          icon='help-about')

    @Slot(bool)
    def about(self, checked=None):
        """Display the dialog showing the about for TypeAtlas."""
        dialog = TypeAtlasAbout(self.mainWindow)
        dialog.exec_()

    @Slot(bool)
    def aboutFreeType(self, checked=None):
        """Display the dialog showing the about for FreeType."""
        dialog = FreeTypeAbout(self.mainWindow, self.freeTypeVersion)
        dialog.exec_()

    @Slot(bool)
    def aboutFontConfig(self, checked=None):
        """Display the dialog showing the about for fontconfig."""
        dialog = FontConfigAbout(self.mainWindow, self.fontConfigVersion)
        dialog.exec_()

    @Slot(bool)
    def aboutSystem(self, checked=None):
        """Display the dialog showing the about for the system."""
        dialog = SystemAbout(self.mainWindow)
        dialog.exec_()

    @Slot(bool)
    def aboutPython(self, checked=None):
        """Display the dialog showing the about for Python."""
        dialog = PythonAbout(self.mainWindow)
        dialog.exec_()

    @Slot(bool)
    def aboutQt(self, checked=None):
        """Display the dialog showing the about for Qt."""
        QtWidgets.QMessageBox.aboutQt(self.mainWindow)

