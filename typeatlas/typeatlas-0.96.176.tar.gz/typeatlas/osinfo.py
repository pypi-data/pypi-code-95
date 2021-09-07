# -*- coding: utf-8 -*-
#
#    TypeAtlas Operating System Information
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
#                                 ***
#
#    Alternatively, you may use this file (part of TypeAtlas libraries)
#    under the terms of the X11/MIT license as follows:
#
#    Permission is hereby granted, free of charge, to any person
#    obtaining a copy of this software and associated documentation
#    files (the "Software"), to deal in the Software without
#    restriction, including without limitation the rights to use,
#    copy, modify, merge, publish, distribute, sublicense, and/or sell
#    copies of the Software, and to permit persons to whom the
#    Software is furnished to do so, subject to the following
#    conditions:
#
#    The above copyright notice and this permission notice shall be
#    included in all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#    OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#    WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#    OTHER DEALINGS IN THE SOFTWARE.
#

# License note:
#
# If the compat module is loaded, this module will use Qt and PyQt or PySide
# to acquire the storage drive list, the mounted volume list, the icon theme
# search paths and the current theme name. At the time of writing Qt and PySide
# were licensed under the GNU LGPL, and PyQt was under the GNU GPL.
#
# Be mindful of that. If in doubt, the Qt code can be stripped by searching
# for qtcompat

"""Module with information about the operating system, such as supported font
types, icon finder, drive finder, etc."""

from typeatlas.foreign import appdirs
from collections import namedtuple
import re
import os
import os.path
import sys
import platform
import traceback
import configparser
from operator import attrgetter
from distutils.version import LooseVersion as version_key
#from packaging.version import parse as version_key

from typeatlas.util import warnmsgf, generic_type
from typeatlas.langutil import _, N_
from typeatlas import proginfo

IteratorOf = generic_type('Iterator')
IterableOf = generic_type('Iterable')
SequenceOf = generic_type('Sequence')


FREETYPE_COLR_VERSION_MIN = '2.10.0'

WINDOWS_COLR_VERSION_MIN = '8.1'
WINDOWS_SVG_VERSION_MIN = '10'

# FIXME: I see conflicting reports that these work in macOS 10.14, with
#        COLR/CPAL fonts as early as 10.13.
# Sources: https://yoksel.github.io/color-fonts-demo/
#          https://bugzilla.mozilla.org/show_bug.cgi?id=1425812
#          https://en.wikipedia.org/w/index.php?title=OpenType&oldid=1008183155#Color
DARWIN_COLR_VERSION_MIN = '17.0.0'
DARWIN_SVG_VERSION_MIN = '18.0.0'


OsLogo = namedtuple('OsLogo', 'icon font symbol')

LINUX_PSEUDO_FILESYSTEM = set([
    'anon_inodefs', 'autofs', 'bdev', 'binfmt_misc', 'cgroup', 'cgroup2',
    'configfs', 'cpuset', 'debugfs', 'devfs', 'devpts', 'devtmpfs', 'dlmfs',
    'efivarfs', 'fuse.gvfsd-fuse', 'fuse.gvfs-fuse-daemon', 'fusectl',
    'hugetlbfs', 'mqueue', 'nfsd', 'none', 'overlay', 'pipefs', 'proc',
    'pstore', 'ramfs', 'rootfs', 'rpc_pipefs', 'securityfs', 'sockfs',
    'spufs', 'sysfs', 'tmpfs'
])

# Optical filesystems on Linux and macOS, including the response of psutil
# on Windows.
OPTICAL_FILESYSTEM = set(['udf', 'iso9660', 'cdrom', 'cd9660', 'cdfs'])
NETWORK_FILESYSTEM = set(['remote', 'nfs', 'nfs3', 'nfs4', 'cifs', 'smbfs',
                          'ncpfs', '9p'])

# psutil on Windows only
REMOVABLE_FILESYSTEMS = set(['removable'])


is_windows = False
is_posix = False
is_linux = False
is_darwin = False

if sys.platform.startswith('linux'):
    if platform.dist()[0].lower() == 'ubuntu':
        oslogo = OsLogo(None, 'Ubuntu', u'\uE0FF')
    #oslogo = OsLogo('distributor-logo', None, None)
    oslogo = OsLogo(None, 'Linux Libertine O', u'\uE000')
    is_posix = True
    is_linux = True
elif sys.platform == 'darwin':
    oslogo = OsLogo(None, None, u'\uF8FF')
    is_posix = True
    is_darwin = True
elif sys.platform == 'win32':
    oslogo = OsLogo(None, 'Wingdings', u'\uF0FF')
    is_windows = True
elif os.name == 'posix':
    is_posix = True
    oslogo = OsLogo('distributor-logo', None, None)
else:
    oslogo = OsLogo(None, None, None)


_UNSPECIFIED = object()

_freetype_version = _UNSPECIFIED


def freetype_version() -> str:
    """Get the version of freetype currently installed on the system."""

    global _freetype_version
    if _freetype_version is not _UNSPECIFIED:
        return _freetype_version

    try:
        import ctypes
    except ImportError:
        _freetype_version = None
        return _freetype_version

    try:
        freetype = ctypes.CDLL('libfreetype.so.6')
    except (TypeError, OSError):
        _freetype_version = None
        return _freetype_version

    ft = ctypes.pointer(ctypes.c_voidp(1))

    major = ctypes.pointer(ctypes.c_int(1))
    minor = ctypes.pointer(ctypes.c_int(1))
    patch = ctypes.pointer(ctypes.c_int(1))

    if freetype.FT_Init_FreeType(ft) != 0:
        _freetype_version = None
        return _freetype_version

    try:
        freetype.FT_Library_Version(ft.contents, major, minor, patch)

        _freetype_version = '%d.%d.%d' % (major.contents.value,
                                          minor.contents.value,
                                          patch.contents.value)

    finally:
        freetype.FT_Done_FreeType(ft.contents)

    return _freetype_version


_layered_fonts_supported = None


def layered_fonts_supported() -> bool:
    """Return True if the platform supports CPAL/COLR layered fonts.
    The value may be False on platforms that do."""

    global _layered_fonts_supported
    if _layered_fonts_supported is not None:
        return _layered_fonts_supported

    if is_windows:
        _layered_fonts_supported = (version_key(platform.version()) >=
                                    version_key(WINDOWS_COLR_VERSION_MIN))
    elif is_darwin:
        _layered_fonts_supported = (version_key(platform.release()) >=
                                    version_key(DARWIN_COLR_VERSION_MIN))
    elif is_posix:
        # FIXME: Check features?
        version = freetype_version()
        _layered_fonts_supported = (version_key(version) >=
                                    version_key(FREETYPE_COLR_VERSION_MIN))
    else:
        _layered_fonts_supported = False

    return _layered_fonts_supported


_svg_fonts_supported = None


def svg_fonts_supported() -> bool:
    """Return True if the platform supports SVG fonts. The value may be
    False on platforms that do."""

    global _svg_fonts_supported
    if _svg_fonts_supported is not None:
        return _svg_fonts_supported

    if is_windows:
        _svg_fonts_supported = (version_key(platform.version()) >=
                                version_key(WINDOWS_SVG_VERSION_MIN))
    elif is_darwin:
        _svg_fonts_supported = (version_key(platform.release()) >=
                                version_key(DARWIN_SVG_VERSION_MIN))
    elif is_posix:
        # FreeType does not yet support SVG fonts
        _svg_fonts_supported = False
    else:
        _svg_fonts_supported = False

    return _svg_fonts_supported


class StorageLocation(object):

    def __init__(self, path: str, label: str=None, icon: str='folder'):
        if label is None:
            label = path

        self.path = path
        self.label = label
        self.icon = icon


class StorageLocations(object):

    def __init__(self, *args, **kwargs):
        super(StorageLocations, self).__init__(*args, **kwargs)

        try:
            import psutil
        except ImportError:
            self.psutil = None
        else:
            self.psutil = psutil

        self.win32api = None

        if is_windows:
            try:
                import win32api
            except ImportError:
                win32api = None
            self.win32api = win32api

        self.qtcompat = sys.modules.get('typeatlas.compat')

    def drives(self) -> IteratorOf[StorageLocation]:
        """Yield the disk drives of the computer, e.g. flash drives."""
        if self.win32api is not None:
            for drive in self.win32api.GetLogicalDriveStrings().split('\0'):
                if not drive:
                    continue
                path = os.path.normpath(drive + ':\\')
                yield StorageLocation(path, _('Drive %s') % (path, ),
                                      icon='drive-harddisk')
            return

        if self.qtcompat is not None:
            for fi in self.qtcompat.QtCore.QDir.drives():
                path = os.path.normpath(str(fi.absoluteFilePath()))
                yield StorageLocation(path, _('Drive %s') % (path, ),
                                      icon='drive-harddisk')


    def locations(self) -> IteratorOf[StorageLocation]:
        """Yield the special storage locations on the computer, e.g. homedir."""
        seen = set()
        seen_devs = set()

        homedir = os.path.expanduser('~')
        seen.add(homedir)

        if os.path.exists(homedir):
            yield StorageLocation(homedir, _('Home directory %s') % (homedir, ),
                                  icon='user-home')

        if is_posix and '/' not in seen:
            seen.add('/')
            yield StorageLocation('/', _('Root /'), icon='system')

        if self.psutil is not None:
            for disk in sorted(self.psutil.disk_partitions(all=True),
                               key=attrgetter('mountpoint')):

                if disk.mountpoint in seen:
                    seen_devs.add(disk.device)
                    continue
                if disk.device in seen_devs:
                    seen.add(disk.mountpoint)
                    continue

                seen.add(disk.mountpoint)
                seen_devs.add(disk.device)

                fstype = disk.fstype.lower()

                if fstype in LINUX_PSEUDO_FILESYSTEM:
                    continue

                if not os.access(disk.mountpoint, os.X_OK):
                    continue

                options = disk.opts.split(',')

                if fstype in OPTICAL_FILESYSTEM or 'cdrom' in options:
                    label = _('Optical drive %s') % (disk.mountpoint, )
                    icon = 'drive-optical'

                elif fstype in NETWORK_FILESYSTEM or 'remote' in options:
                    label = _('Remote folder %s') % (disk.mountpoint, )
                    icon = 'folder-remote'

                elif (fstype in REMOVABLE_FILESYSTEMS or
                      (is_linux and '/media/' in disk.mountpoint) or
                      'removable' in options):

                    label = _('Removable drive %s') % (disk.mountpoint, )
                    icon = 'drive-removable-media'

                else:
                    if is_windows:
                        label = _('Drive %s') % (disk.mountpoint, )
                    else:
                        label = _('Mountpoint %s') % (disk.mountpoint, )
                    icon = 'drive-harddisk'

                yield StorageLocation(disk.mountpoint, label, icon )

        elif is_windows:
            for drive in self.drives():
                if drive.path in seen:
                    continue
                yield drive

        elif self.qtcompat is not None:
            for storage in self.qtcompat.QtCore.QStorageInfo.mountedVolumes():
                if storage.rootPath() in seen:
                    continue
                yield StorageLocation(storage.rootPath(), storage.displayName(),
                                      icon='folder')


_icon_search_paths = None


ThemeIconInfo = namedtuple('ThemeIconInfo', 'name context')


def find_icons(theme_name: str=None,
               search_paths: SequenceOf[str]=None,
               inherit: bool=False,
               parse_theme: bool=True, strict: bool=False,
               skip: IterableOf[str]=None,
               include_ours: bool=True,
               hide_duplicates: bool=True) -> IteratorOf[ThemeIconInfo]:
    """Find the icons from a given theme in the given search paths,
    and yield ThemeIconInfo named tuples.

    The theme name and paths are guessed if not passed. If
    Qt is loaded, it is used to acquire them.

    If inherit is True, theme inheritance is observed to an extend,
    but the result is slower. If parse_theme is False, no attempt
    is made to parse the theme, resulting in incorrect context.
    A skip iterable can be passed to skip certain icons, this is
    mainly used so that this function can recurse.

    If strict=True is passed, configparser errors will be propagated.
    """

    global _icon_search_paths

    if theme_name is None or search_paths is None:
        qtcompat = sys.modules.get('typeatlas.compat')
    else:
        qtcompat = None

    if theme_name is None:
        if qtcompat is not None:
            theme_name = qtcompat.QtGui.QIcon.themeName()
        else:
            theme_name = 'hicolor'

    if search_paths is None:
        search_paths = []

        if _icon_search_paths is not None:
            search_paths = _icon_search_paths

        elif qtcompat is not None:
            search_paths = qtcompat.QtGui.QIcon.themeSearchPaths()

        elif os.name == 'posix':
            seen_paths = set()

            for icon_dir in [
                        appdirs.user_data_dir('icons'),
                        appdirs.site_data_dir('icons'),
                        '/usr/share/icons',
                        '/usr/local/share/icons',
                        os.path.expanduser('~/.icons')]:

                if (icon_dir and icon_dir not in seen_paths and
                    os.path.isdir(icon_dir)):

                        search_paths.append(icon_dir)
                        seen_paths.add(icon_dir)

            _icon_search_paths = tuple(search_paths)

    seen = set(skip or ())

    if include_ours:
        try:
            files = os.listdir(proginfo.PROGRAM_ICON_DIR)
        except OSError as exc:
            warnmsgf("Could not get our icons from %s: %s: %s",
                     proginfo.PROGRAM_ICON_DIR, type(exc).__name__, exc)
        else:
            for filename in files:
                basename, ext = os.path.splitext(filename)
                filepath = os.path.join(proginfo.PROGRAM_ICON_DIR, filename)
                if os.path.isfile(filepath) and ext:
                    yield ThemeIconInfo(basename, proginfo.PROGRAM_SHORT_NAME)


    for root in search_paths:
        theme_path = os.path.join(root, theme_name)
        if not os.path.exists(theme_path):
            continue

        inherited_themes = []
        directory_context = {}
        has_index_theme = False

        # Try to extract icon contexts and inherited themes from
        # the index.theme file
        theme_index = os.path.join(theme_path, 'index.theme')
        if parse_theme and os.path.exists(theme_index):
            parser = configparser.RawConfigParser(strict=False)
            try:
                parser.read_file(open(theme_index))
                for section in parser.sections():
                    if section == 'Icon Theme':
                        if 'inherits' in parser.options(section):
                            inherited_themes.extend(
                                    parser.get(section, 'inherits')
                                          .split(','))
                        continue
                    if 'context' not in parser.options(section):
                        continue

                    reldir = os.path.normpath(section)
                    directory_context[reldir] = parser.get(section, 'context')
                has_index_theme = True

            except (configparser.Error, OSError, UnicodeError) as exc:
                if strict:
                    raise
                warnmsgf("Could not read theme index %s: %s: %s",
                         theme_index, type(exc).__name__, exc)
                traceback.print_exc()

        for dirname, dirnames, filenames in os.walk(theme_path):
            reldir = os.path.normpath(os.path.relpath(dirname, theme_path))
            context = directory_context.get(reldir)

            dirnames.sort(key=lambda s: s.casefold())
            filenames.sort(key=lambda s: s.casefold())

            # Try to guess from directory name, somehow
            if context is None:
                # If this didn't path didn't exist in index.theme, ignore.
                if has_index_theme:
                    continue

                components = [comp
                              for comp in reldir.split(os.sep)
                              if not re.match('[0-9]+(?:x[0-9]+)?$', comp)]
                if components:
                    context = os.sep.join(components)
                else:
                    context = 'misc'
                directory_context[reldir] = context

            for filename in filenames:
                if hide_duplicates:
                    filepath = os.path.join(dirname, filename)
                    if os.path.islink(filepath):
                        target = os.path.normpath(os.path.join(
                                    dirname, os.readlink(filepath)))
                        if (os.path.normpath(dirname) == os.path.normpath(
                                os.path.commonpath([target, dirname]))):
                            continue

                basename, ext = os.path.splitext(filename)
                if basename in seen:
                    continue

                seen.add(basename)
                yield ThemeIconInfo(basename, context)

        if inherit and inherited_themes:
            for inherited_theme in inherited_themes:
                for icon_info in find_icons(theme_name, search_paths,
                                            inherit=False, # FIXME ???
                                            parse_theme=parse_theme,
                                            strict=strict, skip=seen,
                                            hide_duplicates=hide_duplicates):
                    seen.add(icon_info.name)
                    yield icon_info
