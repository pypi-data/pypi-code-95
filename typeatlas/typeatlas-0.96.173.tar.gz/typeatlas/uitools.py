# -*- coding: utf-8 -*-
#
#    TypeAtlas User Interface Tools
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

"""Various GUI functions and classes (for e.g. Qt)"""

from __future__ import division
from typeatlas.compat import QtCore, QtGui, QtWidgets, QtModelProxies
from typeatlas.compat import QtNetwork, Qt, Slot, Signal, QT_VERSION
from typeatlas.compat import qtGetBytes
from typeatlas import compat
from typeatlas import external
from typeatlas import fontlist, proginfo
from typeatlas.util import warnmsgf, debugmsg, generic_type, MaybeLazy, Bool
from typeatlas.util import STRIKE
from typeatlas.event import isnoisy
from typeatlas.external import ON_DEMAND
from itertools import count
from collections.abc import Set, Sequence, Mapping, Hashable, Callable
import email.utils
import re
import sys
import time
import inspect
import numbers
import collections
import collections.abc
import os
import os.path
import errno
import contextlib
import traceback
import typeatlas

SequenceOf = generic_type('Sequence')
MappingOf = generic_type('Mapping')
Union = generic_type('Union')
Literal = generic_type('Literal')
Optional = generic_type('Optional')
IterableOf = generic_type('Iterable')
IteratorOf = generic_type('Iterator')
TupleOf = generic_type('Tuple')
AnyStr = generic_type('AnyStr')


CSS_WEIGHT_BOLD = 700
CSS_WEIGHT_NORMAL = 400
CSS_STRETCH_UNSTRETCHED = QtGui.QFont.Unstretched
CSS_STRETCH_CONDENSED = QtGui.QFont.Condensed

# Some versions of Qt have problems here?
FIX_SCROLL_EVENTS = False

# The amount of time to wait after typing in a search box before searching
TYPING_DELAY = 300

# The amount of time to wait after typing to record search term in history
HISTORY_DELAY = 4000


N_ = lambda s: s

_UNSPECIFIED = object()

iconWidths = [16, 22, 32, 48, 64, 96, 128, 192, 256, 384, 512, 768, 1024]
iconHeights = iconWidths
iconSizes = list(map(QtCore.QSize, iconWidths, iconHeights))

_icon_cache = {}
_icon_html_cache = {}
_image_cache = {}
_image_html_cache = {}

_id_generator = count(0)


checkStateToBool = {Qt.Checked: True, Qt.Unchecked: False,
                    Qt.PartiallyChecked: None}

boolToCheckState = {v: k for k, v in checkStateToBool.items()}


def httpDateToTimestamp(date: str) -> int:
    """Convert HTTP date to a timestamp."""
    tpl = email.utils.parsedate(date)
    if tpl is None:
        return None
    return time.mktime(tpl)


# TODO: Will chose those later.
_iconSubstitutions = {
    'select-language': 'preferences-desktop-locale',
    'select-sample':  'document-edit',
    'select-categories': 'folder',
    'typeatlas-sampler': 'fonts',
    'typeatlas-grid': 'fonts',
    'typeatlas-duel': 'fonts',
}

def getIcon(name: str, ext: str='.svgz') -> QtGui.QIcon:
    """Get the icon object for the given icon name.

    That looks in:
        - Substitutions for some icons.
        - Icons shipped with TypeAtlas. If the name contains a slash,
          only icons shipped with TypeAtlas are checked.
        - The icon theme if we're running on GNU/Linux desktop environment,
          or if an icon theme was shipped with TypeAtlas.
        - For name prefixed with char: try to get an Emoji, either
          a standard Unicode one, or one from a specific font.

    """

    name = _iconSubstitutions.get(name, name)

    name = name.replace('/', os.path.sep)
    if name in _icon_cache:
        return _icon_cache[name]

    ours = False

    prefix = proginfo.PROGRAM_ICON_DIR

    iconpath = os.path.join(prefix, name + ext)
    if os.path.isfile(iconpath):

        # If we are using a dark theme, use light icons
        if hasDarkBackground():
            prefixDark = os.path.join(prefix, 'dark')
            pathDark = os.path.join(prefixDark, name + ext)
            if os.path.isfile(pathDark):
                prefix = prefixDark
                iconpath = pathDark

        icon = QtGui.QIcon(iconpath)
        ours = True

    elif os.path.exists(name):
        icon = QtGui.QIcon(name)
    else:

        # Try Emoji icon first.
        match = re.match(r'char:(?:(.)|[uU]\+?([0-9a-fA-F]+))(?::(.*))?$',
                         name)
        if match:
            from typeatlas import fontgrid
            char = match.group(1)
            if not char:
                try:
                    char = chr(int(match.group(2), 16))
                except OverflowError:
                    char = None
            if char:
                font = match.group(3)
                fontInfo = _defaultFontFamilies.get(font)
                return fontgrid.CharacterIconEngine(char,
                                                    fontInfo=fontInfo).icon()

        icon = QtGui.QIcon.fromTheme(name)

    if ours:
        for sz in reversed([16]):
            extrapath = os.path.join(proginfo.PROGRAM_ICON_DIR,
                                     '%dx%d' % (sz, sz),
                                     name + ext)
            if os.path.exists(extrapath):
                size = QtCore.QSize(sz, sz)
                pixmap = QtGui.QIcon(extrapath).pixmap(size)
                icon.addPixmap(pixmap)
                icon.addPixmap(pixmap, icon.Selected)
                icon.addPixmap(pixmap, icon.Active)

    _icon_cache[name] = icon
    return icon


_defaultFontFamilies = {}

def setDefaultFontFamilies(families: SequenceOf[fontlist.FontFamily]):
    """Set the default font families, after they have been gotten
    from the disk by the finder. This makes more font icons work."""
    _defaultFontFamilies.clear()
    for family in families:
        _defaultFontFamilies[family.family] = family


IconPair = collections.namedtuple('IconPair', 'onIcon offIcon')


def getSelectableIconPair(onName: str, offName: str=None,
                          *args, **kwargs) -> IconPair:
    """Get a selectable icon pair for actions, one icon for
    when the action is checked, and one when it is not checked.

    You can either provide two icon names, in which case one
    will be used for the off icon, and another for the on icon.

    Or you can provide a single icon, which will be paired with a
    grayed out disabled icon using the DisabledIconEngine for its
    off icon.

    The return value of this class is accepted by the icon=
    argument of the action() method of Toolbox class, and can
    also be used with the DualIconAction().
    """
    onIcon = getIcon(onName, *args, **kwargs)
    if offName is not None:
        offIcon = getIcon(offName, *args, **kwargs)
    else:
        offIcon = DisabledIconEngine(onIcon).icon()
    return IconPair(onIcon, offIcon)


def getImage(name: str, ext: str='.svgz') -> QtGui.QIcon:
    """Return an image shipped with TypeAtlas as a QIcon."""
    name = name.replace('/', os.path.sep)
    if name in _image_cache:
        return _image_cache[name]

    if '.' in name:
        iconpath = os.path.join(proginfo.PROGRAM_IMAGE_DIR, name)
    else:
        iconpath = os.path.join(proginfo.PROGRAM_IMAGE_DIR, name + ext)
    if os.path.exists(iconpath):
        icon = QtGui.QIcon(iconpath)
    elif os.path.exists(name):
        icon = QtGui.QIcon(name)
    else:
        icon = QtGui.QIcon()

    _image_cache[name] = icon
    return icon


def getIconUrl(name: str, ext: str='.svgz') -> str:
    """Get the URL for a given icon shipped with TypeAtlas
    for use with Qt stylesheets."""
    if '.' not in name:
        name = name + ext

    prefix = proginfo.PROGRAM_ICON_DIR
    iconpath = os.path.join(prefix, name)
    iconurl = 'typeatlas/icons/' + name

    if os.path.isfile(iconpath):

        # If we are using a dark theme, use light icons
        if hasDarkBackground():
            prefixDark = os.path.join(prefix, 'dark')
            pathDark = os.path.join(prefixDark, name + ext)
            if os.path.isfile(pathDark):
                prefix = prefixDark
                iconpath = pathDark

        return iconurl

    #elif os.path.exists(name):
    #    return QtCore.QUrl.fromLocalFile(name).toString()

    else:
        raise OSError(errno.ENOENT, os.strerror(errno.ENOENT), iconpath)


def getImageUrl(name: str, ext: str='.svgz') -> str:
    """Get the URL for a given image shipped with TypeAtlas
    for use with Qt stylesheets."""
    if '.' in name:
        iconpath = os.path.join(proginfo.PROGRAM_IMAGE_DIR, name)
        iconurl = 'typeatlas/images/' + name

    else:
        iconpath = os.path.join(proginfo.PROGRAM_IMAGE_DIR, name + ext)
        iconurl = 'typeatlas/images/' + name + ext

    if os.path.exists(iconpath):
        return iconurl

    #elif os.path.exists(name):
    #    return QtCore.QUrl.fromLocalFile(name)

    else:
        raise OSError(errno.ENOENT, os.strerror(errno.ENOENT), iconpath)


_includeExcludeCheckboxCss = None


def includeExcludeCheckboxCss() -> str:
    """Get CSS suitable for tristate checkboxes that include and exclude."""

    global _includeExcludeCheckboxCss

    # If you think it is ugly
    #return ''

    if _includeExcludeCheckboxCss is None:
        try:
            cssBody = []

            actions = {'checked': 'include', 'unchecked': 'exclude',
                       'indeterminate': 'noaction'}
            suffixes = {'': '', ':disabled': '-disabled',
                        ':hover': '-hover', ':pressed': '-pressed'}

            for checked, action in actions.items():
                for style, suffix in suffixes.items():

                    name = 'widgets/item-{}-matching{}'.format(action, suffix)
                    url = getIconUrl(name)

                    for widget in ['QCheckBox', 'QListView']:
                        cssBody.append(
                            '{}::indicator:{}{} {{ image: url({}); }}\n'
                            .format(widget, checked, style, url))

        except FileNotFoundError:
            _includeExcludeCheckboxCss = ''

        else:
            size = generalSize(refSize=14)
            spacing = int(round(generalHeight(refSize=4)))
            extra = int(round(generalHeight(refSize=2)))

            for widget in ['QCheckBox', 'QListView']:
                cssBody.append(
                    '{}::indicator {{ width: {}px; height: {}px; }}\n'
                    .format(widget, size.height(), size.width()))

            cssBody.append('QCheckBox {{ spacing: {}px; }}\n'.format(spacing))
            cssBody.append('QListView::item {{ min-height: {}px; }}'
                           .format(size.height() + extra));

            _includeExcludeCheckboxCss = ''.join(cssBody)

    return _includeExcludeCheckboxCss


def qFontToCss(font: QtGui.QFont, fontItem: fontlist.FontLike=None,
               qt: bool=False) -> str:
    """Generate CSS for a Qt font.

    If qt=True is passed, the value is intended as Qt stylesheet, not
    HTML stylesheet, and condensed fonts will not be supported."""

    template = '''
        font-family: %s;
        font-style: %s;
        font-weight: %d;
        font-stretch: %s;
    '''

    style = font.style()
    if style == QtGui.QFont.StyleNormal:
        css_style = 'normal'
    elif style == QtGui.QFont.StyleItalic:
        css_style = 'italic'
    elif style == QtGui.QFont.StyleOblique:
        css_style = 'oblique'

    # FIXME: see tag: zjsZ0zzunjo
    factor = ((CSS_WEIGHT_BOLD - 400) /
                (QtGui.QFont.Bold - QtGui.QFont.Normal))
    weight = ((font.weight() - int(QtGui.QFont.Normal)) * factor + 400)

    stretch = font.stretch()
    family = font.family()

    # There's a Qt bug preventing it from working with condensed font, so
    # use our fontItem instead.
    if not qt and fontItem is not None:
        factor = ((CSS_STRETCH_UNSTRETCHED - CSS_STRETCH_CONDENSED) /
                    (fontlist.WIDTH_NORMAL - fontlist.WIDTH_CONDENSED))
        stretch = ((fontItem.width - fontlist.WIDTH_NORMAL) * factor
                                   + CSS_STRETCH_UNSTRETCHED)
        stretch = int(stretch)

        ## FIXME: Ugly workaround for DejaVu Sans Condensed.
        #if (stretch < 0.95 * CSS_STRETCH_UNSTRETCHED and
        #    stretch > 1.05 * CSS_STRETCH_CONDENSED):
        #        stretch = '"semi-condensed"'


    result = template % (family, css_style, int(weight), stretch)
    if qt:
        result = re.sub(r'font-stretch:\s*\d+;', '', result)

    return result


def fontItemToCss(font: fontlist.FontLike, qt: bool=False) -> str:
    """Generate CSS for a typeatlas.fontlist.Font.

    If qt=True is passed, the value is intended as Qt stylesheet, not
    HTML stylesheet, and condensed fonts will not be supported.

    Do not trust this function to be 100% accurate.
    """

    template = '''
        font-family: %s;
        font-style: %s;
        font-weight: %d;
        font-stretch: %d;
    '''

    ## FIXME: Those are probably wrong.
    #if font.slant >= fontlist.SLANT_OBLIQUE:
    #    css_style = 'oblique'
    #elif font.slant >= fontlist.SLANT_ITALIC:
    #    css_style = 'italic'
    #else:
    #    css_style = 'normal'

    # I improvised these:
    if 2 * font.slant >= fontlist.SLANT_OBLIQUE + fontlist.SLANT_ITALIC:
        css_style = 'oblique'
    elif 2 * font.slant >= fontlist.SLANT_ITALIC + fontlist.SLANT_NORMAL:
        css_style = 'italic'
    else:
        css_style = 'normal'

    factor = ((CSS_WEIGHT_BOLD - CSS_WEIGHT_NORMAL) /
                (fontlist.WEIGHT_BOLD - fontlist.WEIGHT_NORMAL))
    weight = ((font.weight - fontlist.WEIGHT_NORMAL) * factor
                           + CSS_WEIGHT_NORMAL)

    factor = ((CSS_STRETCH_UNSTRETCHED - CSS_STRETCH_CONDENSED) /
                (fontlist.WIDTH_NORMAL - fontlist.WIDTH_CONDENSED))
    stretch = ((font.width - fontlist.WIDTH_NORMAL) * factor
                           + CSS_STRETCH_UNSTRETCHED)

    result = template % (font.family, css_style, int(weight),
                         int(stretch))
    if qt:
        result = re.sub(r'font-stretch:\s*\d+;', '', result)

    return result


def defaultFontPointSize() -> int:
    """Return a default point size for fonts to use."""
    font = QtGui.QFont()
    return font.pointSize()


def defaultFontPixelHeight() -> int:
    """Return a default font pixel height to use."""
    font = QtGui.QFont()
    return QtGui.QFontMetrics(font).height()


def screenDpi() -> TupleOf[int, int]:
    """Return the screen DPI."""
    widget = QtWidgets.QWidget()
    return widget.logicalDpiX(), widget.logicalDpiY()

def screenApproxDpi() -> int:
    """Return the screen DPI as a single integer.
    This will be wrong on screens with non-square pixels."""
    widget = QtWidgets.QWidget()
    return (widget.logicalDpiX() + widget.logicalDpiY()) / 2


def pixelsForPt(font: QtGui.QFont=None) -> float:
    """Return the amount of pixels for points. Ballpark."""
    if font is None:
        font = QtGui.QFont()
    else:
        font = QtGui.QFont(font)
    font.setPointSize(96)
    points = font.pointSize()
    if points < 0:
        points = 12
    if points < 1:
        points = 1
    height = QtGui.QFontMetrics(font).height()

    return height / points


def generalLength(pointSize: numbers.Real=None,
                  inches: numbers.Real=None,
                  refSize: numbers.Real=None) -> numbers.Real:
    """Return some general size in pixels, computed from a
    requested size of yours.

    You can use pointSize= to specify the size in points,
    or inches= to specify it in inches, or refSize to specify
    it in unscaled pixels on reference 96 dpi screen.
    """

    if pointSize is not None:
        return pixelsForPt() * pointSize

    if inches is not None:
        return screenApproxDpi() * inches

    if refSize is not None:
        return pixelsForPt() * refSize / 1.5

    return pixelsForPt() * 450


def iconWidth(num: int=None, factor: numbers.Real=None,
              pointSize: numbers.Real=None, inches: numbers.Real=None,
              refSize: numbers.Real=None) -> int:
    """Return an icon width in pixels for a given requested size.
    You can use any of the sizes accepted by generalLength (points,
    inches, pixel size on a 96 DPI screen).

    You can also use the number pointing to the consecutive icon
    size of the preset icon sizes, or a factor that is computed
    against the size of the default system font (for displaying
    an icon next to text)."""

    if num is not None:
        smallestSize = defaultFontPixelHeight()
        offset = min(range(len(iconWidths)),
                     key=lambda i: abs(iconWidths[i] - smallestSize))
        i = num + offset
        i = max(0, min(len(iconWidths) - 1, i))
        return iconWidths[i]

    if refSize is not None:
        num = min(range(len(iconWidths)),
                  key=lambda i: abs(iconWidths[i] - refSize))
        return iconWidth(num=num)

    if factor is not None:
        wantedSize = defaultFontPixelHeight() * factor

    elif pointSize is not None or inches is not None:
        wantedSize = generalLength(pointSize=pointSize, inches=inches)

    else:
        wantedSize = 16

    return min(abs(wantedSize - sz) for sz in iconWidths)


iconHeight = iconWidth


def iconSize(*args, **kwargs) -> QtCore.QSize:
    """Return an icon size. See iconWidth() for help."""
    sz = iconWidth(*args, **kwargs)
    return QtCore.QSize(sz, sz)


def generalWidth(pointSize: numbers.Real=None, inches: numbers.Real=None,
                 refSize: numbers.Real=None,
                 portion: numbers.Real=None) -> numbers.Real:
    """Return a width in pixels of a general object (window, image,
    splash, window).

    You can use any of the sizes accepted by generalLength (points,
    inches, pixel size on a 96 DPI screen).

    You can also use portion=0.8 to specify the portion of the
    screen to be occupied. That probably won't work on more secure
    desktops for which this is a privacy concern. Wayland?"""
    if portion is not None:
        desktop = QtWidgets.QApplication.desktop()
        return portion * desktop.screenGeometry().width()

    if pointSize is not None or inches is not None or refSize is not None:
        return generalLength(pointSize=pointSize, inches=inches,
                             refSize=refSize)

    return QtWidgets.QWidget().width()


def generalHeight(pointSize: numbers.Real=None, inches: numbers.Real=None,
                  refSize: numbers.Real=None,
                  portion: numbers.Real=None) -> numbers.Real:
    """Return a height in pixels of a general object (window, image,
    splash, window). See the help in generalWidth()."""

    if portion is not None:
        desktop = QtWidgets.QApplication.desktop()
        return portion * desktop.screenGeometry().height()

    if pointSize is not None or inches is not None or refSize is not None:
        return generalLength(pointSize=pointSize, inches=inches,
                             refSize=refSize)

    return QtWidgets.QWidget().height()


def generalSize(*args, **kwargs) -> QtCore.QSize:
    """Return a size in pixels of a general object (window, image,
    splash). See the help in generalWidth()."""

    return QtCore.QSize(generalWidth(*args, **kwargs),
                        generalHeight(*args, **kwargs))


def hasDarkBackground(palette: QtGui.QPalette=None) -> bool:
    """Return True if we are using a dark theme."""
    if palette is None:
        #palette = QtGui.QPalette()
        palette = QtWidgets.QApplication.palette()

    text = palette.color(palette.Text)
    base = palette.color(palette.Base)

    return text.value() > base.value()


def matchingInverseColor(color: QtGui.QColor,
                         palette: QtGui.QPalette=None) -> QtGui.QColor:
    """Get the matching inverse color."""
    if palette is None:
        #palette = QtGui.QPalette()
        palette = QtWidgets.QApplication.palette()

    text = palette.color(palette.Text)
    base = palette.color(palette.Base)

    textVal = text.value()
    baseVal = base.value()
    colorVal = color.value()

    textDiff = abs(colorVal - textVal)
    baseDiff = abs(colorVal - baseVal)

    if textDiff < baseDiff:
        if baseDiff >= 64:
            return base
    else:
        if textDiff >= 64:
            return text

    if textVal > 128:
        return QtGui.QColor('black')
    else:
        return QtGui.QColor('white')


def getIconHtml(icon: str, size: Union[int, float, QtCore.QSize],
                ext: str='.svgz') -> str:
    """Get the HTML of a given icon at a given size. This can use
    a data URL, or an URL referring to a file."""
    if isinstance(size, (int, float)):
        size = QtCore.QSize(size, size)

    if isinstance(icon, str):
        key = icon, size.width(), size.height()
        if key not in _icon_html_cache:
            _icon_html_cache[key] = pixmapToHtml(
                    getIcon(icon, ext=ext).pixmap(size))
        return _icon_html_cache[key]
    return pixmapToHtml(icon.pixmap(size))


def getImageHtml(icon: str, size: Union[int, float, QtCore.QSize],
                 ext: str='.svgz') -> str:
    """Get the HTML of a given image at a given size. This can use
    a data URL, or an URL referring to a file."""
    if isinstance(size, (int, float)):
        size = QtCore.QSize(size, size)

    if isinstance(icon, str):
        key = icon, size.width(), size.height()
        if key not in _image_html_cache:
            _image_html_cache[key] = pixmapToHtml(
                    getImage(icon, ext=ext).pixmap(size))
        return _image_html_cache[key]
    return pixmapToHtml(icon.pixmap(size))


def pixmapToHtml(imageOrPixmap: Union[QtGui.QPixmap, QtGui.QImage,
                                      QtGui.QPicture]) -> str:
    """Convert an image or pixmap to HTML using a data URL."""

    buf = QtCore.QBuffer()
    buf.open(QtCore.QIODevice.WriteOnly)

    imageOrPixmap.save(buf, 'PNG', quality=100)
    imageData = qtGetBytes(buf.data().toBase64()).decode('ascii')

    return '<img src="data:image/png;base64,%s" width="%d" height="%d">' % (
                    imageData, imageOrPixmap.width(), imageOrPixmap.height())


WidgetOrItem = Union[QtWidgets.QWidget, QtWidgets.QLayoutItem]

def layoutIterate(layout: QtWidgets.QLayout,
                  itemType: type=None,
                  recursive: bool=False, topdown: bool=True,
                  widgets: bool=False) -> IteratorOf[WidgetOrItem]:

    """Yield the items from the QLayout.

    If recursive=True is passed, also yield any items in child layouts.
    They are yielded top-down unless topdown=False is passed.

    To get widgets instead of items, pass widgets=True.

    If you do any modifications to the layout, including anything that might
    trigger a signal causing such modifications, while iterating, better
    convert the result to a list.
    """

    for i in range(layout.count()):
        item = layout.itemAt(i)

        if not topdown and recursive:
            subLayout = item.layout()
            if subLayout is not None:
                yield from layoutIterate(subLayout, itemType,
                                         recursive=True, topdown=topdown,
                                         widgets=widgets)

        if itemType is None or isinstance(item, itemType):
            if not widgets:
                yield item
            else:
                widget = item.widget()
                if widget is not None:
                    yield widget

        if topdown and recursive:
            subLayout = item.layout()
            if subLayout is not None:
                yield from layoutIterate(subLayout, itemType,
                                         recursive=True, topdown=topdown,
                                         widgets=widgets)


def modelIterate(model: QtCore.QAbstractItemModel,
                 index: QtCore.QModelIndex=None,
                 columnCount: int=None) -> IteratorOf[QtCore.QModelIndex]:
    """Iterate over the indexes in a model."""

    if index is None:
        index = QtCore.QModelIndex()

    if index.isValid():
        yield index
        if columnCount is None:
            columnCount = 1

    else:
        columnCount = model.columnCount(index)

    if not model.hasChildren(index):
        return

    rowCount = model.rowCount(index)
    for row in range(rowCount):
        for col in range(columnCount):
            child = model.index(row, col, index)
            if col > 0:
                if child.isValid():
                    yield child
                continue
            else:
                for descendant in modelIterate(model, child, columnCount):
                    yield descendant


IndexRectType = TupleOf[QtCore.QModelIndex, QtCore.QModelIndex]

def modelIterateChildrenRect(model: QtCore.QAbstractItemModel,
                             index: QtCore.QModelIndex=None,
                             columnCount: int=None, depth: int=0,
                             maxDepth: int=float('inf')) -> IndexRectType:
    """Iterate over rectangles of children in the model. A rectangle
    is specified by its top-left corner and bottom-right corner."""

    if index is None:
        index = QtCore.QModelIndex()

    if not model.hasChildren(index):
        return

    if index.isValid():
        if columnCount is None:
            columnCount = 1
    else:
        columnCount = model.columnCount(index)

    rowCount = model.rowCount(index)

    yield (model.index(0, 0, index),
           model.index(rowCount - 1, columnCount - 1, index))

    if depth >= maxDepth:
        return

    for row in range(rowCount):
        child = model.index(row, 0, index)
        for subrect in modelIterateChildrenRect(model, child, columnCount,
                                                depth+1, maxDepth):
            yield subrect


def mimeDataCopy(mime: QtCore.QMimeData) -> QtCore.QMimeData:
    """Return a copy of the mime data."""
    copy = QtCore.QMimeData()
    for mimeFormat in mime.formats():
        value = mime.data(mimeFormat)
        if mimeFormat.startswith('application/x-qt'):
            if '"' in mimeFormat:
                mimeFormat = mimeFormat.split('"')[1]
            if "'" in mimeFormat:
                mimeFormat = mimeFormat.split("'")[1]
        copy.setData(mimeFormat, value)
    return copy


IconModeState = TupleOf[QtGui.QIcon, int, int]

class StateChangedIconEngineBase(QtGui.QIconEngine):

    """A base class for modifying icons in given states.

    Subclasses should implement getIconModeState.
    """

    def icon(self) -> QtGui.QIcon:
        """Return icon backed by this engine."""
        return QtGui.QIcon(self)

    def getIconModeState(self, mode: int, state: int) -> IconModeState:
        """For the given icon and state, return the icon and what mode and
        state to render it in."""
        raise NotImplementedError

    def actualSize(self, size, mode, state):
        icon, mode, state = self.getIconModeState(mode, state)
        return icon.actualSize(size, mode, state)

    def availableSizes(self, mode, state):
        icon, mode, state = self.getIconModeState(mode, state)
        return icon.availableSizes(mode, state)

    def paint(self, painter, rect, mode, state):
        icon, mode, state = self.getIconModeState(mode, state)
        icon.paint(painter, rect, Qt.AlignCenter, mode, state)

    def pixmap(self, size, mode, state):
        icon, mode, state = self.getIconModeState(mode, state)
        return icon.pixmap(size, mode, state)


class DisabledIconEngine(StateChangedIconEngineBase):

    """Create a disabled font engine which displays the icon
    always in the disabled state if it is inactive, otherwise
    it displays it normally."""

    def __init__(self, icon: QtGui.QIcon):
        super().__init__()
        self.origIcon = icon

    def getIconModeState(self, mode: int, state: int) -> IconModeState:
        #if state == QtGui.QIcon.Off:
        if mode != QtGui.QIcon.Active:
            return self.origIcon, QtGui.QIcon.Disabled, state
        return self.origIcon, mode, state


class DualIconAction(QtWidgets.QAction):
    """Return an action that swaps its own icon when it is
    toggled. You need to provide an IconPair instead of QIcon."""

    def __init__(self, iconPair: IconPair, *args, **kwargs):
        self.iconPair = iconPair
        super().__init__(iconPair.offIcon, *args, **kwargs)
        self.toggled.connect(self._swapIcon)

    @Slot(bool)
    def _swapIcon(self, checked: bool):
        self.setIcon(self.iconPair.onIcon
                        if checked
                        else self.iconPair.offIcon)


class Toolbox(QtCore.QObject):

    """A box of tools. You spit out actions from the actionDefinitions,
    you can then add them to toolbars and menu with populateToolbar()
    or populateMenu()."""

    actionDefinitions = []

    def __init__(self, *args, **kwargs):
        super(Toolbox, self).__init__(*args, **kwargs)

        self._counter = count(0)

        self.actionsEnabled = True
        self.actions = []
        self.actionGroups = {}
        self.actionByKey = {}

        self.currentGroup = None

        definitions = self.actionDefinitions
        if callable(definitions):
            definitions = definitions()

        getNextAction = lambda oldAction: next(definitions)

        if isinstance(definitions, collections.abc.Iterator):
            if inspect.isgenerator(definitions):
                getNextAction = definitions.send

        elif isinstance(definitions, collections.abc.Iterable):
            definitions = iter(definitions)

        action = None

        while True:
            try:
                action = getNextAction(action)
            except StopIteration:
                break

            if isinstance(action, tuple):
                action = self.action(*action)
            elif isinstance(action, dict):
                action = self.action(**action)

            self.actions.append(action)

    @property
    def actionParent(self) -> QtCore.QObject:
        """The parent of the actions. The default is self,
        you can override in a subclass."""
        return self

    @contextlib.contextmanager
    def group(self, name: Hashable=None, exclusive: bool=False,
                    parent: QtCore.QObject=None):
        """Return a context manager to be used within actionDefinitions
        to group actions under a group of a given name, optionally exclusive."""
        if parent is None:
            parent = self.actionParent

        if name in self.actionGroups:
            group = self.actionGroups[name]

        else:
            group = QtWidgets.QActionGroup(parent)
            if exclusive:
                group.setExclusive(True)

            if name is None:
                name = 'UnnamedGroup-%d' % (next(self._counter, ))

            if name is not None:
                self.actionGroups[name] = group

        self.currentGroup = group
        try:
            yield group
        finally:
            self.currentGroup = None

    def separator(self, key: Hashable=None,
                        parent: QtCore.QObject=None) -> QtWidgets.QAction:
        """Add a separator."""
        if parent is None:
            parent = self.actionParent
        action = QtWidgets.QAction(parent)
        action.setSeparator(True)
        if key is not None:
            self.actionByKey[key] = action
        return action

    def action(self, slot: Union[Callable, str]=None,
                     text: str=None,
                     icon: Union[QtGui.QIcon, str, IconPair]=None,
                     key: Hashable=None, parent: QtCore.QObject=None,
                     checkable: bool=False, checked: bool=False,
                     shortcut: str=None,
                     shortcutContext: int=Qt.WidgetWithChildrenShortcut,
                ) -> QtWidgets.QAction:

        """Add an action.

        You can specify a slot (either a name of a method of the toolbox, or
        a callable object as supported by Qt signals and QAction().

        The icon can be specified as a string, QIcon, IconPair, etc.
        You can specify a shortcut using a key sequence string.
        You can alias the action with a key.

        You can make the action checkable and/or checked.

        You can put the action in a group using the group() context manager.

        """

        iconPair = None

        if parent is None:
            parent = self.actionParent

        if text is None and slot is None and icon is None:
            return self.separator(key, parent)

        elif isinstance(icon, tuple):
            iconPair = icon
            icon = iconPair.onIcon if checked else iconPair.offIcon
            action = DualIconAction(iconPair, text, parent)

        elif icon is not None:
            if isinstance(icon, str):
                icon = getIcon(icon)
            action = QtWidgets.QAction(icon, text, parent)
        else:
            action = QtWidgets.QAction(text, parent)

        if slot is not None:
            if callable(slot):
                action.triggered.connect(slot)
            else:
                action.triggered.connect(getattr(self, slot))

        if key is not None:
            self.actionByKey[key] = action

        if checkable:
            action.setCheckable(True)
        if checked:
            action.setChecked(True)
        if shortcut:
            if isinstance(shortcut, str):
                shortcut = QtGui.QKeySequence.fromString(shortcut)
            action.setShortcut(shortcut)
            if shortcutContext is not None:
                action.setShortcutContext(shortcutContext)

        if self.currentGroup is not None:
            self.currentGroup.addAction(action)

        return action

    def disableActions(self, group: Hashable=None, action: Hashable=None):
        """Disable the actions from the specified group, or the specific
        action by key."""
        if group is not None:
            self.actionGroups[group].setDisabled(True)
        elif action is not None:
            self.actionByKey[action].setDisabled(True)
        else:
            if not self.actionsEnabled:
                return
            for action in self.actions:
                action.setDisabled(True)
            self.actionsEnabled = False
       
    def enableActions(self, group: Hashable=None, action: Hashable=None):
        """Enable the actions from the specified group, or the specific
        action by key."""
        if group is not None:
            self.actionGroups[group].setDisabled(False)
        elif action is not None:
            self.actionByKey[action].setDisabled(False)
        else:
            if self.actionsEnabled:
                return
            for action in self.actions:
                action.setDisabled(False)
            self.actionsEnabled = True

    def addContextMenu(self, widget: QtWidgets.QWidget):
        """Add the toolbox actions as a context meny of the specified
        widget."""
        widget.setContextMenuPolicy(Qt.ActionsContextMenu)
        widget.addActions(self.actions)
    
    def populate(self, widget: QtWidgets.QWidget):
        """Populate the provided menu or toolbar with the actions of
        the toolbox."""
        for action in self.actions:
            widget.addAction(action)

    populateMenu = populateToolbar = populate


def makeDragDropClass(parent: type=QtWidgets.QWidget,
                      name: str='DragDropWidget',
                      defaultDragEnabled: bool=True,
                      defaultDropEnabled: bool=False,
                      defaultMimeTypes: SequenceOf[str]=()) -> type:

    """Return a drag & drop widget type.

    You specify the type of widget you do need, its name, and
    whether drag and drop need to be enabled by default. For drag,
    if mime data is not set, the drag is disabled.

    You can specify default mime types.

    To use this widget connect to dataDropped or call setDragMimeData().
    """

    class DragDropWidget(parent):

        """A drag and drop widget of a specified type.

        To use this widget connect to dataDropped or call setDragMimeData()."""

        def __init__(self, *args, dragEnabled: bool=defaultDragEnabled,
                                  dropEnabled: bool=defaultDropEnabled,
                                  mimeTypes: SequenceOf[str]=defaultMimeTypes,
                                  **kwargs):

            super().__init__(*args, **kwargs)
            self._dragMimeData = None
            self._dragEnabled = bool(dragEnabled)
            self._dropEnabled = bool(dropEnabled)
            self._mimeTypes = list(mimeTypes)
            self._dragStartPos = None

            if self._dropEnabled:
                self.setAcceptDrops(True)

        @Slot(QtCore.QMimeData)
        def setDragMimeData(self, value: MaybeLazy[QtCore.QMimeData]):
            """Set the mime data. This can be either the original mime data,
            or a callable that returns it for lazy evaluation."""
            self._dragMimeData = value

        def produceDragMimeData(self) -> QtCore.QMimeData:
            """Return the mime data for the class, requesting it from
            the lazy callable if needed."""
            mimeData = self._dragMimeData
            if callable(mimeData):
                return mimeData()
            elif mimeData is not None:
                return mimeDataCopy(mimeData)
            else:
                return None

        def setDragEnabled(self, value: bool):
            """Enable or disable drag."""
            self._dragEnabled = bool(value)

        def dragEnabled(self) -> bool:
            """Return True if drag is enabled."""
            if self._dragEnabled and self._dragMimeData is not None:
                return True
            return False

        def setDropEnabled(self, value: bool):
            """Enable or disable drops."""
            self._dropEnabled = bool(value)
            self.setAcceptDrops(self._dropEnabled)

        def dropEnabled(self) -> bool:
            """Return True if drops are enabled."""
            return self._dropEnabled

        def supportedDragActions(self) -> int:
            """We support copy action. The widget can't disappear (be moved)."""
            return Qt.CopyAction

        def supportedDropActions(self):
            """We support copy action. The widget can't disappear (be moved)."""
            if self.dropEnabled():
                return Qt.CopyAction
            else:
                return Qt.IgnoreAction

        def mousePressEvent(self, event):
            if not self.dragEnabled():
                return

            if event.button() == Qt.LeftButton:
                self._dragStartPos = event.pos()

        def mimeTypes(self):
            return self._mimeTypes

        def mouseMoveEvent(self, event):
            if self._dragStartPos is None:
                return

            if not self.dragEnabled():
                return

            if not event.buttons() & Qt.LeftButton:
                return

            mouseShift = (event.pos() - self._dragStartPos).manhattanLength()

            if mouseShift < QtWidgets.QApplication.startDragDistance():
                return

            mimeData = self.produceDragMimeData()
            if mimeData is None:
                return

            drag = QtGui.QDrag(self)
            drag.setMimeData(mimeData)

            drag.exec(self.supportedDragActions())


        def _handleEvent(self, event, drop=False):
            supported = self.supportedDropActions()
            possible = event.possibleActions()
            remaining = possible & supported

            if not remaining:
                return

            mimeData = event.mimeData()
            if not any(mimeData.hasFormat(mimetype)
                       for mimetype in self.mimeTypes()):
                return

            if drop:
                self.handleDroppedData(mimeData)

            if not event.proposedAction() & supported:
                bits = bin(int(remaining)).partition('b')[2]
                for i, v in enumerate(reversed(bits)):
                    if v == '0':
                        continue
                    event.setDropAction(Qt.DropAction(1 << i))
                    event.accept()
                    return

            event.acceptProposedAction()

        dataDropped = Signal(QtCore.QMimeData)

        def handleDroppedData(self, mimeData: QtCore.QMimeData):
            """Emit the dataDropped signal. Connect to it to use the widget."""
            self.dataDropped.emit(mimeData)

        def dragEnterEvent(self, event):
            return self._handleEvent(event, drop=False)

        def dropEvent(self, event):
            return self._handleEvent(event, drop=True)

    DragDropWidget.__name__ = name

    return DragDropWidget


DragDropWidget = makeDragDropClass()
DragDropLabel = makeDragDropClass(QtWidgets.QLabel, 'DragDropLabel')


def flipWheelEvent(event: QtCore.QEvent,
                   alwaysHorizontal: bool=False) -> QtCore.QEvent:
    """Flip horizontal and vertical scroll of an event.
    Usually needed only because older Qt sucks."""

    if QT_VERSION == 4:
        if alwaysHorizontal or event.orientation() == Qt.Vertical:
            orientation = Qt.Horizontal
        else:
            orientation = Qt.Vertical

        event = QtGui.QWheelEvent(event.pos(), event.globalPos(),
                                  event.delta(), event.buttons(),
                                  event.modifiers(), orientation)

    else:
        # Handle the new fancy Qt functionality that breaks continuous scroll
        # mice, and makes mouse scroll generally not work due to integer
        # overflows, and the general Qt bugginess.
        angleDelta = event.angleDelta()
        angleDelta = QtCore.QPoint(angleDelta.y(), angleDelta.x())
        pixelDelta = event.pixelDelta()

        # Absurdly, we need to provide the deprecated members, although
        # they aren't provided to us. Qt is a pile of steaming garbage.
        # There isn't even any docs to how they differ. Putting some arbitrary
        # values - no docs means arbitrary values are acceptable, besides,
        # Qt provides arbitrary values for mouse wheel, so why shouldn't we
        # pass arbitrary values back?
        vertical = not angleDelta.isNull() and angleDelta.y()
        horizontal = not angleDelta.isNull() and angleDelta.x()

        if not vertical and not horizontal:
            return event

        if alwaysHorizontal:
            orientation = Qt.Horizontal
            delta = max([angleDelta.y(), angleDelta.x()], key=abs)
            angleDelta = QtCore.QPoint(delta, 0)
            pixels = max([pixelDelta.y(), pixelDelta.x()], key=abs)
            pixelDelta = QtCore.QPoint(pixels, 0)

        elif vertical and horizontal:
            if angleDelta.y() > angleDelta.x():
                orientation = Qt.Vertical
                delta = angleDelta.y()
            else:
                orientation = Qt.Horizontal
                delta = angleDelta.x()

        elif vertical:
            orientation = Qt.Vertical
            delta = angleDelta.y()
        else:
            orientation = Qt.Horizontal
            delta = angleDelta.x()

        pixelDelta = QtCore.QPoint(pixelDelta.y(), pixelDelta.x())

        args = []
        for attr in ['phase', 'source', 'inverted']:
            if not hasattr(event, attr):
                break
            args.append(getattr(event, attr)())

        event = QtGui.QWheelEvent(event.posF(), event.globalPosF(),
                                  pixelDelta, angleDelta,
                                  delta, orientation,
                                  event.buttons(),
                                  event.modifiers(), *args)
    return event


class FlippableListView(QtWidgets.QListView):

    """A list view whose scroll can be flipped if FIX_SCROLL_EVENTS
    is True. The need for that may depend on Qt version."""

    def __init__(self, *args, **kwargs):
        self._flipScroll = False
        super().__init__(*args, **kwargs)

    @Slot(bool)
    def setFlipScroll(self, value: bool=False):
        """Set whether the scroll flip would be requested."""
        self._flipScroll = bool(value)

    def flipScroll(self) -> bool:
        """Return True if scroll flip is requested."""
        return self._flipScroll

    def wheelEvent(self, event):
        if FIX_SCROLL_EVENTS and self._flipScroll:
            event = flipWheelEvent(event)
        return super().wheelEvent(event)


class _QtProcessCallbacks(QtCore.QObject):

    """A callbacks object needed used by the Qt executor. It contains the
    slots needed to process data from a subprocess, and its exit status.

    Needed are the executor, the process, the callbacks that should be
    called once we complete, and a process ID to remove from the executor.

    The executor takes care of connecting the signals.
    """

    def __init__(self, executor: external.Executor,
                       process: QtCore.QProcess,
                       callbacks: external.CallCallbacks=None,
                       processId: int=None):
        super().__init__()
        self.executor = executor
        self.process = process
        self.bufsize = getattr(callbacks, 'bufsize', None) or 256 * 1024
        self.processId = processId
        if callbacks is None:
            self.callbacks = None
        else:
            self.callbacks = callbacks.chunked_wrapper()

    @Slot()
    def readyReadStandardOutput(self):
        """Standard output of the process is ready to read. This calls the
        process_stdout() of the callbacks you passed."""
        self.process.setReadChannel(QtCore.QProcess.StandardOutput)
        while True:
            buf = self.process.read(self.bufsize)
            if not buf:
                break
            if self.callbacks is not None:
                self.callbacks.process_stdout(qtGetBytes(buf))

    @Slot()
    def readyReadStandardError(self):
        """Standard error of the process is ready to read. This writes
        the stderr of the process to our stderr. The caller takes care to merge
        the channels if this is not needed."""
        self.process.setReadChannel(QtCore.QProcess.StandardError)
        while True:
            buf = self.process.read(self.bufsize)
            if not buf:
                break
            buf = qtGetBytes(buf)
            encoding = getattr(sys.stderr, 'encoding', None)
            if encoding:
                sys.stderr.write(buf.decode(encoding, 'surrogateescape'))
            else:
                sys.stderr.write(buf)

    @Slot(int, QtCore.QProcess.ExitStatus)
    def finished(self, exitCode: int, exitStatus: int=None):
        """Process ended with the given exit code and Qt exit status.

        If a signal is received, or anything other than QtCore.QProcess.NormalExit,
        this method calls handle_exit() with -0xffff to denote a signal, but
        the actual process won't know what signal was generated.
        """

        if self.processId is not None:
            process, cbs = self.executor.runningProcesses.pop(self.processId)
            process.deleteLater()

        if self.callbacks is not None:
            if (exitStatus is not None and
                exitStatus != QtCore.QProcess.NormalExit):

                self.callbacks.handle_exit(-0xffff)
            else:
                self.callbacks.handle_exit(exitCode)


class QtExecutor(external.Executor, QtCore.QObject):
    """An executor for commands that uses Qt's process facilities and
    supports async calls."""

    def __init__(self, *args, **kwargs):
        super(QtExecutor, self).__init__(*args, **kwargs)
        self.runningProcesses = {}

    def _execParent(self):
        parent = self.parent()
        if parent is None:
            parent = self
        return parent

    def execute(self, call: external.CallDefinition,
                      command: external.ExternalCommand,
                      args: SequenceOf[AnyStr],
                      env: MappingOf[AnyStr, AnyStr]=None,
                      callbacks: external.CallCallbacks=_UNSPECIFIED,
                      wait: 'Union[bool, Literal[ON_DEMAND]]'=_UNSPECIFIED):
        if callbacks is _UNSPECIFIED:
            callbacks = self.callbacks

        args = [arg if isinstance(arg, str) else arg.decode('ascii')
                for arg in args]

        if wait is _UNSPECIFIED:
            wait = call.wait

        process = QtCore.QProcess(self._execParent())

        if not wait or callbacks is None:
            process.startDetached(args[0], args[1:])
            return

        if env is not None and False:
            procenv = QtCore.QProcessEnvironment.systemEnvironment()
            for key, value in env.items():
                procenv.insert(key, value)
            process.setProcessEnvironment(procenv)

        processId = next(_id_generator)
        #process.finished.connect(lambda *args:
        #                             self.runningProcesses.pop(processId))


        if callbacks and callbacks.merge_outputs:
            process.setProcessChannelMode(QtCore.QProcess.MergedChannels)

        process.start(args[0], args[1:], QtCore.QIODevice.ReadOnly)

        if wait and callbacks is not None and not callbacks.require_blocking:

            cbs = _QtProcessCallbacks(self, process, callbacks, processId)
            process.readyReadStandardOutput.connect(cbs.readyReadStandardOutput)
            process.readyReadStandardError.connect(cbs.readyReadStandardError)
            process.finished.connect(cbs.finished)
            self.runningProcesses[processId] = process, cbs

        else:
            # Make sure something happens to stderr.
            cbs = _QtProcessCallbacks(self, process)
            process.readyReadStandardError.connect(cbs.readyReadStandardError)


        if wait and callbacks is not None and callbacks.require_blocking:

            callbacks = callbacks.chunked_wrapper()

            while True:
                ready = process.waitForReadyRead(-1)
                while True:
                    buf = process.read(callbacks.bufsize)
                    if not buf:
                        break
                    callbacks.process_stdout(qtGetBytes(buf))

                #if process.state() == process.NotRunning:
                if not ready:
                    break

            process.waitForFinished(-1)

            if (process.exitStatus() is not None and
                process.exitStatus()!= QtCore.QProcess.NormalExit):
                return callbacks.handle_exit(-0xffff)
            else:
                return callbacks.handle_exit(process.exitCode())


class TransposedModel(QtCore.QAbstractProxyModel):

    """A Qt model proxy that transposes the original model."""

    def setSourceModel(self, model: QtCore.QAbstractItemModel):
        """Set the model being proxied."""
        oldModel = self.sourceModel()
        if oldModel is not None:
            oldModel.modelAboutToBeReset.disconnect(self._beginReset)
            oldModel.modelReset.disconnect(self._endReset)

        self.beginResetModel()
        super().setSourceModel(model)
        self.endResetModel()

        ## WTF? Why do I need to do this?
        model.modelAboutToBeReset.connect(self._beginReset)
        model.modelReset.connect(self._endReset)

    @Slot()
    def _beginReset(self):
        self.beginResetModel()

    @Slot()
    def _endReset(self):
        self.endResetModel()

    def hasChildren(self, parent=QtCore.QModelIndex()):
        return False

    def index(self, row, column, parent=QtCore.QModelIndex()):
        return self.createIndex(row, column)

    def parent(self, index):
        return QtCore.QModelIndex()

    def mapToSource(self, index):
        model = self.sourceModel()
        if model is None or index.parent().isValid():
            return QtCore.QModelIndex()
        return model.index(index.column(), index.row())

    def mapFromSource(self, index):
        if index.parent().isValid():
            return QtCore.QModelIndex()
        return self.index(index.column(), index.row())

    def rowCount(self, parent):
        model = self.sourceModel()
        if model is None or parent.isValid():
            return 0
        return model.columnCount()

    def columnCount(self, parent):
        model = self.sourceModel()
        if model is None or parent.isValid():
            return 0
        return model.rowCount()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        model = self.sourceModel()
        if model is None:
            return None

        if orientation == Qt.Horizontal:
            return model.headerData(section, Qt.Vertical, role)
        else:
            return model.headerData(section, Qt.Horizontal, role)


class RotatedHeaderView(QtWidgets.QHeaderView):

    """A rotated header view in which the headers can be turned at
    right angles. Presently it looks ugly.

    It gets a single extra argument: angle - the rotation angle.
    """

    def __init__(self, *args, angle: numbers.Real=-90, **kwargs):
        super().__init__(*args, **kwargs)
        self.setRotationAngle(angle)

    def rotationAngle(self) -> numbers.Real:
        """Get the rotation angle."""
        return self._angle

    def setRotationAngle(self, angle: numbers.Real):
        """Set the rotation angle."""
        #if angle not in [-90, 90, 180]:
        #    raise ValueError(repr(angle))
        self._angle = angle

    #def sectionSizeHint(self, logicalIndex):
        #hint = super().sectionSizeHint(logicalIndex)
        #return QtCore.QSize(hint.height(), hint.width())

    #def sectionSize(self, logicalIndex):
        #hint = super().sectionSizelogicalIndex()
        #return QtCore.QSize(hint.height(), hint.width())

    def sectionSizeFromContents(self, logicalIndex):
        hint = super().sectionSizeFromContents(logicalIndex)
        if self._angle % 360 in [90, 270]:
            return QtCore.QSize(hint.height(), hint.width())
        elif self._angle % 360 in [0, 180]:
            return hint
        else:
            rect = QtCore.QRect(QtCore.QPoint(0,0), hint)
            center = rect.center()
            transform = QtGui.QTransform()

            transform.translate(center.x(), center.y())
            transform.rotate(float(self._angle))
            transform.translate(-center.x(), -center.y())
            rect = transform.mapRect(rect)
            return rect.size()

        return hint

    def paintSection(self, painter, rect, logicalIndex):
        crazyAngle = self._angle % 360 not in [0, 90, 180, 270]
        painter.save()
        center = rect.center()

        painter.translate(center.x(), center.y())
        painter.rotate(float(self._angle))
        painter.translate(-center.x(), -center.y())

        if not crazyAngle:
            transform = painter.worldTransform()
        else:
            transform = QtGui.QTransform()

            transform.translate(center.x(), center.y())
            transform.rotate(float((self._angle + 45)// 90 * 90))
            transform.translate(-center.x(), -center.y())

        #rect = painter.worldTransform().mapRect(rect)
        #if crazyAngle and False:
        #    painter.setClipRect(painter.worldTransform().mapRect(rect))

        super().paintSection(painter,
                             transform.mapRect(rect),
                             logicalIndex)
        #if crazyAngle:
        #    painter.setClipRect(painter.worldTransform().mapRect(rect))

        painter.restore()


class QuickSearch(QtWidgets.QWidget):

    """A quick search widget that can use a combo box or line edit
    underneath. You can use the searchTriggered signal to connect to
    searches triggered by enter or timeout.

    The quick search has a typingDelay that defines when the search is
    triggered automatcically. You can provide a history, which is updated
    automatically. It has its own historyDelay; until it expires edited
    strings that are similar are considered the same entry and it is replaced.

    You can provide a place holder text.

    You can access the original line edit though self.lineEdit
    """

    searchTriggered = Signal(str)

    def __init__(self, *args,
                       placeholderText: str=None,
                       typingDelay: int=TYPING_DELAY,
                       historyDelay: int=HISTORY_DELAY,
                       history: 'typeatlas.datastore.History'=None,
                       **kwargs):
        super().__init__(*args, **kwargs)

        self.setLayout(QtWidgets.QStackedLayout())

        if history is None or True:
            mainWidget = lineEdit = QtWidgets.QLineEdit()
        else:
            # FIXME: Broken
            mainWidget = QtWidgets.QComboBox()
            mainWidget.setEditable(True)
            lineEdit = mainWidget.lineEdit()

        self.layout().addWidget(mainWidget)

        self.mainWidget = mainWidget
        self.lineEdit = lineEdit

        self.searchText = ''
        self.previousText = ''
        self.typingExpired = True

        self.typingDelay = typingDelay
        self.historyDelay = historyDelay

        self.history = history

        self.timer = timer = QtCore.QTimer()
        timer.setSingleShot(True)

        lineEdit.textChanged.connect(self._textChanged)
        lineEdit.returnPressed.connect(self.triggerSearch)
        timer.timeout.connect(self._textChangeCompleted)

        self.historyTimer = historyTimer = QtCore.QTimer()
        historyTimer.setSingleShot(True)
        historyTimer.timeout.connect(self._disregardHistoryChange)

        if history is not None:
            self.historyModel = StringListModel(history, parent=self)
            completionMode = QtWidgets.QCompleter.PopupCompletion
            if mainWidget is lineEdit:
                completer = QtWidgets.QCompleter(self.historyModel, self)
                completer.setCompletionMode(completionMode)
                mainWidget.setCompleter(completer)
            else:
                lineEdit.completer().setCompletionMode(completionMode)
                mainWidget.setModel(self.historyModel)
                mainWidget.setInsertPolicy(mainWidget.NoInsert)

        if hasattr(lineEdit, 'setClearButtonEnabled'):
            lineEdit.setClearButtonEnabled(True)
            lineEdit.addAction(getIcon('search'), lineEdit.LeadingPosition)
            if self.history is not None and lineEdit is mainWidget:
                action = lineEdit.addAction(getIcon('document-open-recent'),
                                            lineEdit.TrailingPosition)
                action.triggered.connect(completer.complete)

        if placeholderText:
            lineEdit.setPlaceholderText(placeholderText)

        self.setSizePolicy(self.mainWidget.sizePolicy())

    def text(self) -> str:
        """Return the current search text."""
        return self.searchText

    def setText(self, text: str):
        """Set the current search text."""
        self.lineEdit.setText(text)
        self.triggerSearch()

    @Slot()
    def triggerSearch(self):
        """Trigger the search. This means enter was pressed or text was
        set explicitly."""
        self.timer.stop()
        self._textChangeCompleted()
        self.historyTimer.stop()
        self._disregardHistoryChange()

    @Slot()
    def _textChangeCompleted(self):
        """An earlier change to text was accepted, either the timer expired
        or we were explicitly asked to accept the change."""
        self.previousText = previous = self.searchText
        self.searchText = text = self.lineEdit.text()

        if previous == text:
            return

        if self.history is not None and text:

            replacing = None
            if (not self.typingExpired and previous and
                text.startswith(previous)):
                    replacing = previous

            self.history.push(text, replacing)

        self.typingExpired = False
        self.searchTriggered.emit(text)

    @Slot(str)
    def _textChanged(self, text):
        """The line edit was changed, so activate a timer before
        accepting the change."""
        self.timer.start(self.typingDelay)
        self.historyTimer.start(self.historyDelay)

    @Slot()
    def _disregardHistoryChange(self):
        """Too much time passed or entry was explicitly changed, consider
        new changes to be new history entries and record them seperately.
        Do not record them as a change of the old entry, but as a new one.
        """
        self.typingExpired = True



DOWNLOAD_DESTINATION = QtNetwork.QNetworkRequest.User + 0
DOWNLOAD_OUTPUT = QtNetwork.QNetworkRequest.User + 1
DOWNLOAD_QUEUE = QtNetwork.QNetworkRequest.User + 2
DOWNLOAD_CUSTOM = QtNetwork.QNetworkRequest.User + 3


class Downloader(QtCore.QObject):

    """Downloader for objects from the Internet. Use the object
    by calling download() or downloadMany()"""

    def __init__(self, parent=None, bufsize=256 * 1024):
        super(Downloader, self).__init__(parent)
        self.manager = QtNetwork.QNetworkAccessManager(self)
        self.bufsize = bufsize

    started = Signal(int)
    progress = Signal(int)
    finished = Signal(QtNetwork.QNetworkRequest, bool)
    queueFinished = Signal(int, bool)

    def downloadMany(self, iterable: IterableOf[TupleOf[str, AnyStr]],
                           callback: Callable=None) -> int:
        """Download many URLs into many paths. They are specified as
        tuples source url, destination path; so the first argument is
        just an iterable as the downloadables() method returns for
        objects in charinfo and langutil.

        Returns an integer identifier of the queue.

        When the queue is completed, the queueFinished() signal is emitted
        with the queue ID, and its success status.

        Each individual download will emit the finished() signal with
        the request and the success status.
        """
        return self._processQueue(iter(iterable))

    def _processQueue(self, queue: IteratorOf[TupleOf[str, AnyStr]]):
        """Download the next element of the queue."""

        try:
            url, destination = next(queue)
        except StopIteration:
            self.queueFinished.emit(id(queue), True)
            return

        request = self.download(url, destination,
                                attributes={DOWNLOAD_QUEUE: queue})
        return id(queue)

    def _finished(self, request: QtNetwork.QNetworkRequest,
                        successful: bool=True):
        """The network request finished. If we're in the queue,
        process the next one."""
        self.finished.emit(request, successful)
        queue = request.attribute(DOWNLOAD_QUEUE)
        if queue is not None:
            self._processQueue(queue)

    def download(self, url: str, destination: AnyStr,
                       callback: Callable=None,
                       attributes: MappingOf[int, object]=()
                 ) -> QtNetwork.QNetworkRequest:
        """Download the given URL to the given path. That's the
        like the downloadables() tuples provided by langutil and
        charinfo.

        You can provide custom attributes. The callback is presently
        not called.

        When completed, emit the finished() signal with
        the request and the success status.
        """
        request = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
        request.setAttribute(DOWNLOAD_DESTINATION, destination)

        for key, value in dict(attributes).items():
            request.setAttribute(key, value)

        reply = self.manager.head(request)
        reply.finished.connect(self.headReplyFinished)

        return request

    @Slot()
    def headReplyFinished(self):
        request = None
        try:
            reply = self.sender()
            request = reply.request()

            destination = request.attribute(DOWNLOAD_DESTINATION)

            length = reply.header(request.ContentLengthHeader)
            date = reply.header(request.LastModifiedHeader)

            try:
                st = os.stat(destination)

            except EnvironmentError:
                pass

            else:
                timestamp = date.currentMSecsSinceEpoch() / 1000.
                if st.st_size == length and int(st.st_mtime) >= timestamp:
                    self._finished(request, True)
                    return

            output = open(destination, 'wb')

            request.setAttribute(DOWNLOAD_OUTPUT, output)

            self.started.emit(length)

            reply = self.manager.get(request)
            reply.finished.connect(self.downloadReplyFinished)
            reply.readyRead.connect(self.readReady)

        except:
            self._finished(request, False)
            raise

    def downloadReplyFinished(self):
        request = None
        try:
            reply = self.sender()
            request = reply.request()

            output = request.attribute(DOWNLOAD_OUTPUT)

            output.close()
        except:
            self._finished(request, False)
            raise
        else:
            self._finished(request, True)

    def readReady(self):
        reply = self.sender()
        request = reply.request()
        requestId = next(_id_generator)

        output = request.attribute(DOWNLOAD_OUTPUT)

        while True:
            buf = reply.read(self.bufsize)
            if not buf:
                break
            output.write(buf)


ItemItemRole = Qt.UserRole
ItemKeyRole = Qt.UserRole + 1
ItemSearchRole = Qt.UserRole + 2
ItemValueRole = Qt.UserRole + 3


class DictItemAdapter(object):

    """Allows dictionary with label, icon and color keys to be
    used with ObjectItemModelMixin and subclasses."""

    __slots__ = ('data', )

    def __init__(self, data: Mapping):
        self.data = data

    def label(self, styled: bool=False) -> Optional[str]:
        return self.data.get('label')

    def icon(self) -> Optional[str]:
        return self.data.get('icon')

    def color(self) -> Optional[str]:
        return self.data.get('color')

    def search_text(self) -> Optional[str]:
        if 'search_text' not in self.data:
            return self.label()
        return self.data['search_text']

    def style(self) -> Set:
        return frozenset()


class CallMapItemModel(QtCore.QAbstractItemModel):

    """Use callables or named methods in a map to construct a model.

    The method names are defined in a role-to-name dictionary, and
    can be overriden in the constructor through roleMethods.

    Custom callables for each can be called as keyword arguments.

    This defines the following new roles:
        - ItemItemRole - the item itself, implemented by itemAtIndex().
        - ItemKeyRole - the key of the item (item.key), implemented by
                        itemKeyData()
        - ItemSearchRole - the search text (item.search_text()),
                           implemented by searchTextData().
        - ItemValueRole - e.g. the checkbox value for the key, implented
                          by itemValueData()

    """

    defaultRoleMethods = {
        Qt.DisplayRole: 'displayData',
        Qt.DecorationRole: 'decorationData',
        Qt.EditRole: 'editData',
        Qt.ToolTipRole: 'toolTipData',
        Qt.StatusTipRole: 'statusTipData',
        Qt.WhatsThisRole: 'whatsThisData',
        Qt.SizeHintRole: 'sizeHintData',

        Qt.FontRole: 'fontData',
        Qt.TextAlignmentRole: 'textAlignmentData',
        Qt.BackgroundRole: 'backgroundData',
        Qt.ForegroundRole: 'foregroundData',
        Qt.CheckStateRole: 'checkStateData',
        Qt.InitialSortOrderRole: 'initialSortOrderData',

        Qt.AccessibleTextRole: 'accessibleTextData',
        Qt.AccessibleDescriptionRole: 'accessibleDescriptionData',

        ItemItemRole: 'itemAtIndex',
        ItemKeyRole: 'itemKeyData',
        ItemSearchRole: 'searchTextData',
        ItemValueRole: 'itemValueData',
    }

    def __init__(self, *args, roleMethods: MappingOf[int, str]={}, **kwargs):

        possibleRoleMethods = dict(self.defaultRoleMethods)
        possibleRoleMethods.update(roleMethods)

        methodOverrides = {}

        for role, methodName in possibleRoleMethods.items():
            editMethodName = 'set' + methodName[0].upper() + methodName[1:]
            if methodName in kwargs:
                methodOverrides[methodName] = kwargs.pop(methodName)
            if editMethodName in kwargs:
                methodOverrides[editMethodName] = kwargs.pop(editMethodName)

        super().__init__(*args, **kwargs)

        roleMethods = {}
        roleEditMethods = {}

        for role, methodName in possibleRoleMethods.items():

            editMethodName = 'set' + methodName[0].upper() + methodName[1:]

            if hasattr(self, methodName):
                roleMethods[role] = methodName
            if methodName in methodOverrides:
                roleMethods[role] = methodName
                setattr(self, methodName, methodOverrides[methodName])

            if hasattr(self, editMethodName):
                roleEditMethods[role] = editMethodName
            if editMethodName in methodOverrides:
                roleEditMethods[role] = editMethodName
                setattr(self, editMethodName, methodOverrides[editMethodName])

        self.roleMethods = roleMethods
        self.roleEditMethods = roleEditMethods

    def data(self, index, role=Qt.DisplayRole):

        methodName = self.roleMethods.get(role)
        if methodName is None:
            return None

        method = getattr(self, methodName)
        if method is None:
            return None

        if not index.isValid():
            return None

        result = method(index, role)

        if (result is not None and
            role == Qt.DecorationRole and
            isinstance(result, str)):
                return getIcon(result)

        return result

    def setData(self, index, value, role=Qt.EditRole):
        methodName = self.roleEditMethods.get(role)
        if methodName is None:
            return False

        method = getattr(self, methodName)
        if method is None:
            return False

        if not index.isValid():
            return False

        return method(index, value, role)


class ListItemModel(CallMapItemModel):

    """Turn a sequence in a model."""

    def __init__(self, items: Sequence, *args,
                       columnCount: int=1,
                       rowsRemovable: bool=False,
                       itemAdapter: Callable=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.items = items
        self.columnCountValue = columnCount
        self.rowsRemovable = rowsRemovable
        self.itemAdapter = itemAdapter

        if isnoisy(items):

            links = [
                (items.insert_pending, self._insertPending),
                (items.remove_pending, self._removePending),
                (items.inserted, self._insertCompleted),
                (items.removed, self._removeCompleted),
            ]

            for signal, slot in links:
                signal.connect(slot)

    def index(self, row, column, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return QtCore.QModelIndex()
        try:
            item = self.items[row]
        except IndexError:
            return QtCore.QModelIndex()
        else:
            result = self.createIndex(row, column, item)
            return result

    def itemAtIndex(self, index, role=ItemItemRole):
        result = index.internalPointer()
        if self.itemAdapter is not None:
            result = self.itemAdapter(result)
        return result

    def setItemAtIndex(self, index, item, role=ItemItemRole):
        self.items[index.row()] = item

    def parent(self, index):
        return QtCore.QModelIndex()

    def hasChildren(self, parent=QtCore.QModelIndex()):
        if not parent.isValid():
            return True
        return False

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            # FIXME: If this returns 0, all children disappear. WHY?
            # Documentation says it *must* return 0.
            return self.columnCountValue
        return self.columnCountValue

    def rowCount(self, parent=QtCore.QModelIndex()):

        if parent.isValid():
            return 0

        return len(self.items)

    def removeRows(self, row, count, parent=QtCore.QModelIndex()):
        if self.rowsRemovable:
            return False
        if parent.isValid():
            return False
        del self.items[row:row + count]
        return True

    def __repr__(self):
        return '%s(%r, <...>)' % (type(self).__name__, self.items)

    # Noisy methods
    def _insertRemoveAction(self, row, item, insert=True, completed=False):
        ###if completed:
        ###    debugmsg('---', 'insert' if insert else 'remove', row, item)

        if insert:
            method = 'InsertRows'
            actionAttr = 'inserting'
        else:
            method = 'RemoveRows'
            actionAttr = 'removing'

        if not completed:
            getattr(self, 'begin' + method)(QtCore.QModelIndex(), row, row)
        else:
            getattr(self, 'end' + method)()

    def _insertPending(self, *args, **kwargs):
        self._insertRemoveAction(*args, insert=True, completed=False, **kwargs)

    def _insertCompleted(self, *args, **kwargs):
        self._insertRemoveAction(*args, insert=True, completed=True, **kwargs)

    def _removePending(self, *args, **kwargs):
        self._insertRemoveAction(*args, insert=False, completed=False, **kwargs)

    def _removeCompleted(self, *args, **kwargs):
        self._insertRemoveAction(*args, insert=False, completed=True, **kwargs)



class StringModelMixin(CallMapItemModel):

    """A mixin that turns a CallMapItemModel subclass into a
    string model."""

    def __init__(self, *args, editableStrings: bool=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.editableStrings = editableStrings

    def displayData(self, index, role=Qt.DisplayRole):
        return self.itemAtIndex(index)

    def editData(self, index, role=Qt.EditRole):
        if not self.editableStrings:
            return None
        return self.itemAtIndex(index)

    def setEditData(self, index, value, role=Qt.EditRole):
        if not self.editableStrings:
            return False
        self.setItemAtIndex(index, value)
        return True

    def itemKeyData(self, index, role=ItemKeyRole):
        return self.itemAtIndex(index)


class ObjectItemModelMixin(CallMapItemModel):

    """A mixin that turns a CallMapItemModel subclass into a
    model using objects .label(), .icon() and .search_text() methods."""

    def displayData(self, index, role=Qt.DisplayRole):
        return self.itemAtIndex(index).label()

    def decorationData(self, index, role=Qt.DecorationRole):
        item = self.itemAtIndex(index)
        icon = item.icon()
        if icon is not None:
            return getIcon(icon)

        if hasattr(item, 'color'):
            color = item.color()
            if color is not None:
                return QtGui.QColor(color)

        return None

    def searchTextData(self, index, role=ItemSearchRole):
        item = self.itemAtIndex(index)
        if not hasattr(item, 'search_text'):
            return item.label()
        return item.search_text()

    def itemKeyData(self, index, role=ItemKeyRole):
        item = self.itemAtIndex(index)
        return getattr(item, 'key')

    def backgroundData(self, index, role=ItemSearchRole):
        item = self.itemAtIndex(index)
        if not hasattr(item, 'color'):
            return None

        # Color is displayed as icon in this case. User should select
        # *either* icon or colour, in fact everyone needs to have
        # enough laziness to select only one of them, but should they
        # select both, colour the actual item.
        if item.icon() is None:
            return None

        color = item.color()
        if color is not None:
            return QtGui.QBrush(QtGui.QColor(color))

        return item.search_text()

    def foregroundData(self, index, role=ItemSearchRole):
        item = self.itemAtIndex(index)
        if not hasattr(item, 'color'):
            return None

        # Color is displayed as icon in this case. User should select
        # *either* icon or colour, in fact everyone needs to have
        # enough laziness to select only one of them, but should they
        # select both, colour the actual item.
        if item.icon() is None:
            return None

        color = item.color()
        if color is not None:
            return QtGui.QBrush(matchingInverseColor(QtGui.QColor(color)))

        return item.search_text()


class StyledObjectItemModelMixin(ObjectItemModelMixin):

    """A mixin that turns a CallMapItemModel subclass into a
    model using objects .label(), .icon(), .search_text()
    and .style() methods."""

    def displayData(self, index, role=Qt.DisplayRole):
        return self.itemAtIndex(index).label(styled=True)

    def fontData(self, index, role=Qt.FontRole):
        item = self.itemAtIndex(index)
        style = item.style()
        if style:
            font = QtGui.QFont()
            if STRIKE in style:
                font.setStrikeOut(True)
            return font


class CheckboxItemModelMixin(CallMapItemModel):

    """A mixin that adds checkboxes to a CallMapItemModel from a
    checkValues mapping. Needs to be included after ListItemModel."""

    def __init__(self, checkValues: Mapping,
                       checkFixed: Mapping=None, *args,
                       checkColumn: int=None, isTristate: Bool=False,
                       **kwargs):
        super().__init__(*args, **kwargs)

        self.checkValues = checkValues
        self.checkFixed = checkFixed if checkFixed is not None else {}
        self.checkColumn = checkColumn

        self.isTristate = isTristate

        if isnoisy(checkValues):
            checkValues.added.connect(self._valueChanged)
            checkValues.deleted.connect(self._valueChanged)
            checkValues.value_changed.connect(self._valueChanged)

        if checkFixed is not None and isnoisy(checkFixed):
            checkFixed.added.connect(self._valueChanged)
            checkFixed.deleted.connect(self._valueChanged)
            checkFixed.value_changed.connect(self._valueChanged)

    def checkStateData(self, index, role=Qt.CheckStateRole):
        if (self.checkColumn is not None and
            index.column() == self.checkColumn):
                return None

        key = self.itemKeyData(index)
        if key in self.checkFixed:
            boolValue = self.checkFixed[key]
        else:
            boolValue = self.checkValues.get(key)

        return boolToCheckState.get(boolValue)

    def setCheckStateData(self, index, value, role=Qt.CheckStateRole):
        key = self.itemKeyData(index)
        if key in self.checkFixed:
            return False

        boolValue = checkStateToBool.get(value)
        if boolValue is None:
            self.checkValues.pop(key)
        else:
            self.checkValues[key] = boolValue

        return True

    def itemValueData(self, index, role=Qt.CheckStateRole):
        if (self.checkColumn is not None and
            index.column() == self.checkColumn):
                return None

        key = self.itemKeyData(index)
        if key in self.checkFixed:
            return self.checkFixed[key]
        return self.checkValues.get(key)

    def flags(self, index):
        flags = super().flags(index)
        if index.isValid():
            key = self.itemKeyData(index)
            if key in self.checkFixed:
                flags &= ~Qt.ItemIsEnabled
            if self.isTristate:
                flags |= Qt.ItemIsUserTristate
            return flags | Qt.ItemIsUserCheckable
        return flags

    def _valueChanged(self, key, value, old_value=_UNSPECIFIED):
        changedIndex = None

        # FIXME: SLOW
        for index in self.match(self.index(0, 0),
                                ItemKeyRole, key, 1, Qt.MatchExactly):
            changedIndex = index
            break

        if changedIndex is None:
            warnmsgf("Row not found: %r -> %r", key, value)
            return

        self.dataChanged.emit(changedIndex, changedIndex)


class StringListModel(ListItemModel, StringModelMixin):

    """A Qt model taking a list of strings, optionally a NoisySequence."""


class StyledObjectListModel(ListItemModel,
                            StyledObjectItemModelMixin):

    """A Qt model taking an object list, optionally a NoisySequence."""


class CheckableStyledObjectListModel(ListItemModel,
                                     StyledObjectItemModelMixin,
                                     CheckboxItemModelMixin):

    """A Qt model taking an object list, and a checkbox map.
    Optionally, a NoisySequence and/or NoisyMapping."""
