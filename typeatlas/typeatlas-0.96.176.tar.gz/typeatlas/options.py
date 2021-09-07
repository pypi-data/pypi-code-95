# -*- coding: utf-8 -*-
#
#    TypeAtlas Options Store
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

"""Implementation of program options.

Use Options.getInstance() to get the options.
Use OptionsWidget.getInstance() to get the configuration dialog.
"""

from typeatlas.compat import QtCore, QtGui, QtWidgets, QtModelProxies
from typeatlas.compat import Qt, Slot, Signal, setResizeMode
from collections import namedtuple
from typeatlas.langutil import _, N_, H_, U_, textlang
from typeatlas.uitools import iconSizes, iconSize, generalWidth, generalHeight
from typeatlas.uitools import getIcon
from collections.abc import Callable
from collections import OrderedDict
from typeatlas.util import OrderedSet, Overwriter, generic_type
from typeatlas.util import MaybeLazy
from typeatlas import external, proginfo
import configparser
import shutil
import io
import os
import json
import binascii
from functools import partial

SequenceOf = generic_type('Sequence')
Union = generic_type('Union')
Optional = generic_type('Optional')
Literal = generic_type('Literal')
Any = generic_type('Any')

Choice = namedtuple('Choice', 'value label')
Choice.icon = None

ChoiceType = Union[Choice, Any]

DEFAULT = object()
DefaultType = Union[bool, Literal[DEFAULT]]


_checkboxMap = {Qt.Checked: True, Qt.Unchecked: False,
                Qt.PartiallyChecked: DEFAULT}


### FIXME FIXME FIXME: Default for pixels and stuff should be *NOT PRESENT*
###                    So that when we get bigger monitor, it grows?


class _Args(tuple):
    """A tuple of *args to call the type/class with.

    When returned by a type factory, it means calling the type
    itself with the given *args."""

    __slots__ = ()


def _parseSizeOrPoint(delim: str, factory: Callable, s: str) -> _Args:
    """Parse point or size, separated by a separator like 'x' or ','.
    Return the arguments for QSize or QPoint. You need to provide a
    number factory, like int or float."""

    parts = s.split('x')
    if len(parts) == 1:
        sz = factory(s)
        return _Args((sz, sz))

    if len(parts) == 2:
        return _Args(map(factory, parts))

    raise ValueError("Invalid size or point %r" % (s, ))


# Parsers for the given types
parsers = {
    QtCore.QSize: partial(_parseSizeOrPoint, 'x', int),
    QtCore.QSizeF: partial(_parseSizeOrPoint, 'x', float),
    QtCore.QPoint: partial(_parseSizeOrPoint, ',', int),
    QtCore.QPointF: partial(_parseSizeOrPoint, ',', float),
    bytes: binascii.a2b_base64,
    object: json.loads,
    dict: json.loads,
    list: json.loads,
}


# Dumpers for the given types
dumpers = {
    QtCore.QSize: lambda v: '%sx%s' % (v.width(), v.height()),
    QtCore.QSizeF: lambda v: '%sx%s' % (v.width(), v.height()),
    QtCore.QPoint: lambda v: '%s, %s' % (v.x(), v.y()),
    QtCore.QPointF: lambda v: '%s, %s' % (v.x(), v.y()),
    bytes: lambda v: binascii.b2a_base64(v, newline=False).decode('ascii'),
    object: partial(json.dumps, ensure_ascii=False),
    dict: partial(json.dumps, ensure_ascii=False),
    list: partial(json.dumps, ensure_ascii=False),
}


class Option(object):

    """Config file option."""

    def __init__(self, name: str, section: str, label: str=None,
                       type: type=None,
                       choices: MaybeLazy[SequenceOf[ChoiceType]]=None,
                       default: MaybeLazy[Any]=None,
                       icon: str=None, hasDefault: bool=None,
                       unit: str=None, attribute: str=None,
                       signalAttribute: str=None,
                       fromString: Callable=None, parseString: Callable=None,
                       toString: Callable=None):

        if hasDefault is None:
            #hasDefault = True if choices oeelse False
            hasDefault = True
        self.name = name
        self.section = section
        self.type = type
        self.choices = choices
        self.label = label
        self.icon = icon
        self.default = default
        self.hasDefault = hasDefault

        if parseString is None:
            parseString = parsers.get(type)
        if toString is None:
            toString = dumpers.get(type)

        self.parseString = parseString

        if toString is not None:
            self.toString = toString
        if fromString is not None:
            self.fromString = fromString

        if attribute is None:
            attribute = self.makeAttributeName(name)
        if signalAttribute is None:
            signalAttribute = attribute + 'Changed'
        self.attribute = attribute
        self.signalAttribute = signalAttribute

    def fromString(self, value: str) -> Any:
        """Parse the option value from string, returning a value of
        whose type self.type. This can be overriden with fromString=
        in the constructor. The parseString= can override just the
        parsing, without the construction."""

        if self.parseString is not None:
            value = self.parseString(value)
        if self.type is not None:
            if isinstance(value, _Args):
                value = self.type(*value)
            else:
                value = self.type(value)
        return value

    def toString(self, value: Any) -> str:
        """Convert the value to string. The default implementation just
        calls str() on the value, you can override with toString=
        in the constructor."""
        return str(value)

    def getChoices(self) -> SequenceOf[ChoiceType]:
        """Get the available choices."""
        choices = self.choices
        if choices is FONT_SIZES:
            return QtGui.QFontDatabase.standardSizes()
        if callable(choices):
            choices = choices()
        return choices

    def property(option: 'Option', optionCls: type=None) -> property:
        """Create a property that gets/sets that option through the Options
        object."""
        def getter(self):
            try:
                return self.getValue(option.name, option.section)
            except KeyError:
                raise AttributeError

        def setter(self, value):
            self.setValue(option.name, option.section, value)

        getter.__name__ = option.attribute
        setter.__name__ = option.attribute

        return property(getter, setter)

    def signal(self) -> Signal:
        """Create a signal descriptor that listens for value changes of this option,
        to be placed in the the Options class."""
        if self.type is bytes:
            return Signal(QtCore.QByteArray)
        return Signal(self.type or object)

    @classmethod
    def makeAttributeName(self, value: str) -> str:
        """Return a suitable attribute name for a given option."""
        parts = value.split('-')
        if len(parts) < 2:
            return value
        return parts[0] + ''.join(part.capitalize() for part in parts[1:])

    def _makeChoice(self, choice: ChoiceType,
                          default: MaybeLazy[DefaultType]=False,
                          realValue: Any=None) -> Choice:
        """Return a Choice() object for the given choice."""

        if isinstance(choice, Choice):
            return choice
        if choice is DEFAULT:
            if realValue is not None:
                return Choice(choice, '%s (%s)'
                                % (N_('Default'), self.toString(realValue)))
            return Choice(choice, N_('Default'))
        if choice is None:
            return Choice(choice, N_('Default') if default else N_('Unset'))
        return Choice(choice, self.toString(choice))

    def getCheckbox(self, options: 'OptionsBase',
                          parent: QtWidgets.QWidget=None) -> QtWidgets.QCheckBox:
        """Get a checkbox for this option."""
        checkbox = QtWidgets.QCheckBox(parent)

        checkbox.setText(_(self.label))
        if self.icon:
            checkbox.setIcon(getIcon(self.icon))

        value = options.getRawValue(self.name, self.section)

        default = self.default
        if callable(default):
            default = default()

        if self.hasDefault:
            checkbox.setTristate(True)
            if value is DEFAULT:
                checkbox.setCheckState(Qt.PartiallyChecked)

        if value is not DEFAULT:
            if value:
                checkbox.setCheckState(Qt.Checked)
            else:
                checkbox.setCheckState(Qt.Unchecked)

        @checkbox.stateChanged.connect
        def callback(state):
            options.setDraftValue(self.name, self.section,
                                  _checkboxMap.get(state))
        return checkbox

    def getComboBox(self, options: 'OptionsBase',
                          parent: QtWidgets.QWidget=None) -> QtWidgets.QComboBox:
        """Return a combo box for this option."""
        combo = QtWidgets.QComboBox(parent)
        if self.type is None:
            combo.setEditable(False)
        else:
            combo.setEditable(True)

        values = []

        currentValue = options.getRawValue(self.name, self.section)

        if (currentValue is not None and currentValue is not DEFAULT and
            combo.isEditable()):
                combo.setEditText(self.toString(currentValue))

        if self.hasDefault:

            default = self.default
            if callable(default):
                default = default()

            defaultChoice = self._makeChoice(DEFAULT, default=True,
                                             realValue=default)
            values.append(DEFAULT)

            if combo.isEditable():
                combo.lineEdit().setPlaceholderText(_(defaultChoice.label))

            if defaultChoice.icon:
                combo.addItem(getIcon(defaultChoice.icon),
                              _(defaultChoice.label))
            else:
                combo.addItem(_(defaultChoice.label))

            combo.setEditText('')

        for i, choice in enumerate(self.getChoices() or (), 1):
            choice = self._makeChoice(choice, default=False)
            values.append(choice.value)
            if choice.icon:
                combo.addItem(getIcon(choice.icon), _(choice.label))
            else:
                combo.addItem(_(choice.label))

            if currentValue is not DEFAULT and currentValue == choice.value:
                combo.setCurrentIndex(i)

        @combo.currentIndexChanged.connect
        def indexCallback(index: int):
            if index == -1:
                return
            value = values[index]
            options.setDraftValue(self.name, self.section, value)
            if not combo.isEditable():
                return
            if value is DEFAULT or value is None:
                combo.setEditText('')
            else:
                combo.setEditText(self.toString(value))

        def editCallback():
            value = combo.currentText()
            if not value:
                options.setDraftValue(self.name, self.section, DEFAULT)
                return
            try:
                value = self.fromString(value)
            except (ValueError, TypeError) as exc:
                ## TODO: Changing the index calls this?
                options.setDraftError(self.name, self.section, exc)

            else:
                # TODO: Should be automatic
                # TODO: Better handling of invalid values?
                ##options.clearDraftError(self.name, self.section)
                options.setDraftValue(self.name, self.section, value)

        if combo.isEditable():
            combo.lineEdit().editingFinished.connect(editCallback)

        label = QtWidgets.QLabel()
        label.setTextFormat(Qt.PlainText)
        label.setText(_(self.label) + ':')

        box = QtWidgets.QWidget()
        box.setLayout(QtWidgets.QHBoxLayout())
        box.layout().addWidget(label)
        box.layout().addWidget(combo)

        return box

    def getWidget(self, options: 'OptionsBase',
                        parent: QtWidgets.QWidget=None) -> QtWidgets.QWidget:
        """Return a widget to edit this option."""
        if self.choices:
            return self.getComboBox(options, parent)
        elif issubclass(self.type, bool):
            return self.getCheckbox(options, parent)
        else:
            # TODO: LineEdit?
            return self.getComboBox(options, parent)


FONT_SIZES = lambda: QtGui.QFontDatabase.standardSizes()

options = [

    Option('type-atlas-size', 'window', type=QtCore.QSize,
           default=lambda: QtCore.QSize(generalWidth(refSize=1200),
                                        generalHeight(refSize=800))),
    Option('font-sampler-size', 'window', type=QtCore.QSize,
           default=lambda: QtCore.QSize(generalWidth(refSize=1200),
                                        generalHeight(refSize=800))),
    Option('font-duel-size', 'window', type=QtCore.QSize,
           default=lambda: QtCore.QSize(generalWidth(refSize=800),
                                        generalHeight(refSize=600))),

    Option('glyph-atlas-size', 'window', type=QtCore.QSize,
           default=lambda: QtCore.QSize(generalWidth(refSize=800),
                                        generalHeight(refSize=600))),

    Option('type-atlas-state', 'window', type=bytes, default=b''),
    Option('type-atlas-arrangement', 'window', type=str, default='simple'),
    Option('type-atlas-splitter-state', 'window', type=bytes, default=b''),
    Option('type-atlas-dock-inner-state', 'window', type=dict, default=lambda: {}),
    Option('type-atlas-pane-sizes', 'window', type=dict, default=lambda: {}),

    Option('toolbar-icon-size', 'display',
           N_('Toolbar icon size'),
           type=QtCore.QSize, choices=iconSizes, unit=N_('pixels'),
           default=lambda: iconSize(refSize=16)),
    Option('info-icon-size', 'display',
           N_('Information document icon size'),
           type=QtCore.QSize, choices=iconSizes, unit=N_('pixels'),
           default=lambda: iconSize(refSize=16)),
    Option('info-flag-size', 'display',
           N_('Information document flag size'),
           type=QtCore.QSize, choices=iconSizes, unit=N_('pixels'),
           default=lambda: iconSize(refSize=16)),
    Option('tooltip-icon-size', 'display',
           N_('Tooltip preview icon size'),
           type=QtCore.QSize, choices=iconSizes, unit=N_('pixels'),
           default=lambda: iconSize(refSize=32)),

    Option('list-font-size', 'display',
           N_('List font size'),
           type=int, choices=FONT_SIZES, unit=N_('pt'), default=16),
    Option('sample-font-size', 'display',
           N_('Default sample font size'),
           type=int, choices=FONT_SIZES, unit=N_('pt'), default=32),
    Option('glyph-stack-font-size', 'display',
           N_('Font size of stack comparison'),
           type=int, choices=FONT_SIZES, unit=N_('pt'), default=96),
    Option('preview-font-size', 'display',
           N_('Default preview font size'),
           type=int, choices=FONT_SIZES, unit=N_('pt'), default=16),
    Option('grid-font-size', 'display',
           N_('Default font grid font size'),
           type=int, choices=FONT_SIZES, unit=N_('pt'), default=32),
    Option('char-box-font-size', 'display',
           N_('Font grid preview character size'),
           type=int, choices=FONT_SIZES, unit=N_('pt'), default=48),

    Option('standard-checkboxes', 'display',
           N_("Use standard OS style for all checkboxes"),
           type=bool, default=False),

    Option('qt-version', 'runtime', N_('Preferred Qt version'),
            choices=[
                ## Not really supported, some features (e.g. tags, categories)
                ## require 5 (they can be made usable-ish with 4).
                #Choice('4', U_('Qt 4')),
                Choice('5', U_('Qt 5')),
            ]),
    Option('qt-bindings', 'runtime', N_('Preferred Qt bindings'),
            choices=[Choice('pyqt', U_('PyQt / SIP (Riverbank)')),
                     Choice('pyside', U_('PySide / Shiboken (Qt)'))]),
    Option('qt-style', 'runtime', N_('Qt style'),
           choices=lambda: QtWidgets.QStyleFactory.keys(),
           type=str),

    Option('sample-selection', 'samples', N_('Font sample selection'),
           choices=[Choice('some', N_('Display highlights')),
                    Choice('most', N_('Display all available samples'))]),
    Option('show-sample-name', 'samples', N_('Display the sample name'),
           type=bool, default=True),

    Option('max-sample-fonts', 'samples',
           N_('Maximum fonts in preview'),
           type=int, default=100),
    Option('max-font-grid-fonts', 'samples',
           N_('Maximum fonts in character map'),
           type=int, default=15),

    Option('layered-font-renderer', 'routines',
           N_('Renderer for color layer fonts (CPAL/COLR)'),
           choices=[Choice('os', N_('Operating system')),
                    Choice('internal', N_('Internal renderer'))]),
    Option('svg-font-renderer', 'routines',
           N_('Renderer for SVG color fonts'),
           choices=[Choice('os', N_('Operating system')),
                    Choice('internal', N_('Internal renderer'))]),


]


class OptionsWidget(QtWidgets.QDialog):

    """Edit options dialog window / widget."""

    def __init__(self, options: 'OptionsBase'=None,
                       parent: QtWidgets.QWidget=None):
        super().__init__(parent)

        if options is None:
            options = Options.getInstance()

        self.options = options

        self.setWindowTitle(_('TypeAtlas options'))

        self.general = QtWidgets.QWidget()
        self.generalLayout = layout = QtWidgets.QVBoxLayout()
        self.general.setLayout(self.generalLayout)

        iconLayout = QtWidgets.QVBoxLayout()
        iconBox = QtWidgets.QGroupBox(_('Icon sizes'))
        iconBox.setLayout(iconLayout)
        layout.addWidget(iconBox)

        fontLayout = QtWidgets.QVBoxLayout()
        fontBox = QtWidgets.QGroupBox(_('Font sizes'))
        fontBox.setLayout(fontLayout)
        layout.addWidget(fontBox)

        iconLayout.addWidget(options.getWidget('toolbar-icon-size'))
        iconLayout.addWidget(options.getWidget('info-icon-size'))
        iconLayout.addWidget(options.getWidget('info-flag-size'))
        iconLayout.addWidget(options.getWidget('tooltip-icon-size'))
        fontLayout.addWidget(options.getWidget('list-font-size'))
        fontLayout.addWidget(options.getWidget('sample-font-size'))
        fontLayout.addWidget(options.getWidget('preview-font-size'))
        fontLayout.addWidget(options.getWidget('grid-font-size'))
        fontLayout.addWidget(options.getWidget('char-box-font-size'))
        layout.addWidget(options.getWidget('standard-checkboxes'))
        layout.addWidget(options.getWidget('qt-version'))
        layout.addWidget(options.getWidget('qt-bindings'))
        layout.addWidget(options.getWidget('qt-style'))

        self.behaviour = QtWidgets.QWidget()
        self.behaviourLayout = layout = QtWidgets.QVBoxLayout()
        self.behaviour.setLayout(self.behaviourLayout)

        sampleLayout = QtWidgets.QVBoxLayout()
        sampleBox = QtWidgets.QGroupBox(_('Samples'))
        sampleBox.setLayout(sampleLayout)
        layout.addWidget(sampleBox)

        sampleLayout.addWidget(options.getWidget('sample-selection'))
        sampleLayout.addWidget(options.getWidget('show-sample-name'))
        sampleLayout.addWidget(options.getWidget('max-sample-fonts'))
        sampleLayout.addWidget(options.getWidget('max-font-grid-fonts'))

        colorFontLayout = QtWidgets.QVBoxLayout()
        colorFontBox = QtWidgets.QGroupBox(_('Color fonts'))
        colorFontBox.setLayout(colorFontLayout)
        layout.addWidget(colorFontBox)

        colorFontLayout.addWidget(options.getWidget('layered-font-renderer'))
        colorFontLayout.addWidget(options.getWidget('svg-font-renderer'))

        checkbox = QtWidgets.QCheckBox(_('Enable 3D acceleration'))
        checkbox.setDisabled(True)
        colorFontLayout.addWidget(checkbox)

        self._executableForEdit = {}

        self.externalBox = QtWidgets.QWidget()
        self.externalLayout = QtWidgets.QGridLayout()
        self.externalBox.setLayout(self.externalLayout)

        for i, executable in enumerate(external.commands_by_executable):
            defaultPath = shutil.which(executable)
            label = QtWidgets.QLabel()
            label.setTextFormat(Qt.PlainText)
            label.setText(executable)

            edit = QtWidgets.QLineEdit()
            if defaultPath:
                edit.setPlaceholderText(defaultPath)
            else:
                edit.setPlaceholderText(_('Select executable...'))

            self._executableForEdit[edit] = executable

            if hasattr(edit, 'setClearButtonEnabled'):
                edit.setClearButtonEnabled(True)

            execPath = options.executablePaths.get(executable)
            if execPath:
                edit.setText(execPath)

            edit.editingFinished.connect(self.pathEditEdited)


            button = QtWidgets.QPushButton(_("Browse..."))
            button.clicked.connect(partial(self.browse, edit, defaultPath))

            self.externalLayout.addWidget(label, i, 0, 1, 1)
            self.externalLayout.addWidget(edit, i, 1, 1, 1)
            self.externalLayout.addWidget(button, i, 2, 1, 1)

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.addTab(self.general, _('Interface'))
        self.tabs.addTab(self.behaviour, _('Behaviour'))
        self.tabs.addTab(self.externalBox, _('Dependencies'))

        self.buttonBox = QtWidgets.QDialogButtonBox()

        save = QtWidgets.QPushButton(getIcon('document-save'), _('Save'))
        cancel = QtWidgets.QPushButton(getIcon('dialog-cancel'), _('Cancel'))

        self.buttonBox.addButton(save, self.buttonBox.AcceptRole)
        self.buttonBox.addButton(cancel, self.buttonBox.RejectRole)

        save.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.tabs)
        self.layout().addWidget(self.buttonBox)

        self.accepted.connect(options.save)
        self.rejected.connect(options.rollback)

        self.completed = False

    closed = Signal()

    @Slot()
    def pathEditEdited(self):
        """A path of an external executable was edited. This
        needs to be called from a QLineEdit signal."""

        edit = self.sender()

        executable = self._executableForEdit[edit]
        path = edit.text()

        if not path:
            self.options.executablePaths.pop(executable, None)
        else:
            self.options.executablePaths[executable] = path

    def browse(self, edit: QtWidgets.QLineEdit, defaultPath: str):
        """Browse for an executable's path."""

        dialog = QtWidgets.QFileDialog()
        if defaultPath:
            directory, filename = os.path.split(defaultPath)
            dialog.setDirectory(directory)
            dialog.selectFile(filename)

        dialog.setFilter(QtCore.QDir.Executable | QtCore.QDir.Files)
        if (dialog.exec_()):
            filename = dialog.selectedFiles()[0]
            edit.setText(filename)

    def closeEvent(self, event: QtCore.QEvent):
        r = super().closeEvent(event )
        if event.isAccepted():
            self.closed.emit()
        return r


class OptionsBase(QtCore.QObject):

    """A base class for options that has the implementations, without the
    option list. The options are in the options attribute.

    Use Options.getInstance().
    """

    options = OrderedDict()

    instance = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        values = {option.name: DEFAULT for option in self.options.values()}

        self.temporaryValues = dict(values)
        self.permanentValues = dict(self.temporaryValues)

        self.parser = None
        self.changed = False
        self.pending = False

    @classmethod
    def getInstance(cls) -> 'OptionsBase':
        """Return the singleton instance of the options, or create
        one if there is not one created yet."""
        if cls.instance is None:
            cls.instance = cls()
        return cls.instance

    def fileName(self, create: bool=False) -> Optional[str]:
        """Return the file name of the options. Implement in a subclass."""
        if create:
            raise NotImplementedError
        return None

    @Slot()
    def save(self, file: io.TextIOBase=None):
        """Save the options. If a file is specified, they are saved to it
        instead of the default one."""
        if file is None:
            with Overwriter(self.fileName(create=True), 'w',
                            encoding='utf8') as file:
                self.save(file)
            return

        if self.parser is None:
            parser = configparser.RawConfigParser()
        else:
            parser = self.parser

        self.saveIntoParser(parser)

        parser.write(file)

    @Slot()
    def load(self, file: io.TextIOBase=None):
        """Load the options. If a file is specified, they are loaded from it
        instead from the default one."""
        if file is None:
            filename = self.fileName()
            if filename is None:
                return
            with open(filename, 'r', encoding='utf8') as file:
                self.load(file)
            return

        parser = configparser.RawConfigParser()

        parser.read_file(file)


        self.loadFromParser(parser)

        self.parser = parser

    def makeSectionName(self, section: str) -> str:
        """Format the section name for the config file."""
        return section.capitalize()

    def makeOptionName(self, option: str) -> str:
        """Format the option name for the config file."""
        return option.replace('-', '_')

    def saveIntoParser(self, parser: configparser.RawConfigParser):
        """Save the options into the given config parser object."""
        self.commit()
        sections = OrderedSet(opt.section for opt in self.options.values())

        for section in sections:
            section = self.makeSectionName(section)
            if not parser.has_section(section):
                parser.add_section(section)

        for option in self.options.values():
            section = self.makeSectionName(option.section)
            optionName = self.makeOptionName(option.name)
            if self.permanentValues[option.name] is DEFAULT:
                if parser.has_option(section, optionName):
                    parser.remove_option(section, optionName)
            else:
                parser.set(section, optionName,
                           option.toString(self.permanentValues[option.name]))

        self.changed = False
        self.pending = False

    def loadFromParser(self, parser: configparser.RawConfigParser):
        """Load the options from the given config parser."""
        for option in self.options.values():
            section = self.makeSectionName(option.section)
            optionName = self.makeOptionName(option.name)
            if not parser.has_option(section, optionName):
                continue
            value = parser.get(section, optionName)
            value = option.fromString(value)
            self.permanentValues[option.name] = value
            self.temporaryValues[option.name] = value

        self.changed = False
        self.pending = False

    @classmethod
    def makeClass(cls, name: str, options: SequenceOf[Option]) -> type:
        """Create a class for options using a given list of such."""
        namespace = {}
        namespace['options'] = OrderedDict()
        for option in options:
            namespace['options'][option.name] = option
            namespace[option.attribute] = option.property()
            namespace[option.signalAttribute] = option.signal()

        return type(name, (cls, ), namespace)

    @Slot()
    def commit(self):
        """Confirm any temporary changes. This happens when e.g. the user
        clicks OK in the options dialog. It is automatically triggered
        when one saves them.

        Editing options usually uses setDraftValue() to set a temporary
        value which is confirmed on save, or rolled back on Cancel.
        """
        self.changed = True
        self.permanentValues = dict(self.temporaryValues)
        self.pending = False

    @Slot()
    def rollback(self):
        """Reset any temporary changes back to the values before the change.

        Editing options usually uses setDraftValue() to set a temporary
        value which is confirmed on save, or rolled back on Cancel.

        This triggers signals for the rolled back options.
        """
        sentinel = object()
        for option in self.options.values():
            value = self.temporaryValues[option.name]
            oldValue = self.permanentValues[option.name]
            if value != oldValue:
                self.setDraftValue(option.name, option.section, oldValue)
        self.pending = False

    def setDraftValue(self, option: str, section: str, value: object):
        """Set the draft value for the given option in the given section.

        This triggers signals for the edited options.

        Editing options usually uses setDraftValue() to set a temporary
        value which is confirmed on save, or rolled back on Cancel.
        """
        oldValue = self.temporaryValues[option]

        if value == oldValue:
            return

        self.pending = True

        self.temporaryValues[option] = value

        if value is DEFAULT:
            value = self.options[option].default
            if callable(value):
                value = value()

        getattr(self, self.options[option].signalAttribute).emit(value)

    def setValue(self, option: str, section: str, value: object):
        """Set the value for a given option in a given section.
        This is automatcailly invoked when setting the property.

        This triggers signals for the edited options."""
        self.changed = True
        self.permanentValues[option] = value
        self.setDraftValue(option, section, value)

    def getWidget(self, name: str, *args, **kwargs) -> QtWidgets.QWidget:
        """Get the widget for the given option. All arguments are
        passed to the options's getWidget()."""
        return self.options[name].getWidget(self, *args, **kwargs)

    def getComboBox(self, name: str, *args, **kwargs) -> QtWidgets.QComboBox:
        """Get the combo box for the given option. All arguments are
        passed to the options's getComboBox()."""
        return self.options[name].getComboBox(self, *args, **kwargs)

    def getCheckbox(self, name: str, *args, **kwargs) -> QtWidgets.QCheckBox:
        """Get the check box for the given option. All arguments are
        passed to the options's getCheckbox()."""
        return self.options[name].getCheckbox(self, *args, **kwargs)

    def getValue(self, option: str, section: str) -> object:
        """Get the value of a given option. This always returns the temporary
        value. Or the default, if no value is set."""
        value = self.temporaryValues[option]
        if value is DEFAULT:
            default = self.options[option].default
            if callable(default):
                default = default()
            return default
        return value

    def getRawValue(self, option: str, section: str) -> object:
        """Get the raw value of a given option, without getting the default.
        This always returns the temporary value, and raises a KeyError if one
        is not set."""
        return self.temporaryValues[option]


class Options(OptionsBase.makeClass('Options', options)):

    """The options of typeatlas. Use Options.getInstance() to get them."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.executablePaths = {}
        self.qtStyleChanged.connect(self._qtStyleChanged)

    def fileName(self, create: bool=False) -> str:
        if create:
            if not os.path.exists(proginfo.CONFIG_DIR):
                os.makedirs(proginfo.CONFIG_DIR)
        filename = os.path.join(proginfo.CONFIG_DIR, proginfo.MAIN_CONFIG)
        if not os.path.exists(filename) and not create:
            filename = None
        return filename

    def loadFromParser(self, parser: configparser.RawConfigParser):
        super().loadFromParser(parser)

        section = 'ExternalTools'

        if not parser.has_section(section):
            return

        for option in parser.options(section):
            self.executablePaths[option] = parser.get(section, option)

    def saveIntoParser(self, parser: configparser.RawConfigParser):
        super().saveIntoParser(parser)

        section = 'ExternalTools'

        if not parser.has_section(section):
            parser.add_section(section)

        for option in parser.options(section):
            if option not in self.executablePaths:
                parser.remove_option(section, option)

        for executable, path in self.executablePaths.items():
            parser.set(section, executable, path)

    @Slot(str)
    def _qtStyleChanged(self, style: str):
        """Called when the Qt style has changed in the options. This
        triggers a change in the GUI."""
        QtWidgets.QApplication.setStyle(style)


