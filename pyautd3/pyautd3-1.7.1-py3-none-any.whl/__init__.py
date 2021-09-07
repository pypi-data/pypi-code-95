'''
File: __init__.py
Project: pyautd
Created Date: 11/02/2020
Author: Shun Suzuki
-----
Last Modified: 07/09/2021
Modified By: Shun Suzuki (suzuki@hapis.k.u-tokyo.ac.jp)
-----
Copyright (c) 2020 Hapis Lab. All rights reserved.

'''

import shutil
import zipfile
import tarfile
import os
import os.path
import platform
import glob

import requests

from pyautd3.autd import Gain, Modulation, PointSequence, GainSequence, Link, AUTD, STMController
from pyautd3.native_methods import Nativemethods

__all__ = [
    'AUTDVersion',
    'Gain',
    'AUTDVersion',
    'Modulation',
    'PointSequence',
    'GainSequence',
    'AUTD',
    'Link',
    'STMController']

__version__ = '1.7.1'

_VERSION_TRIPLE = '.'.join(__version__.split('.')[0:3])
_PLATFORM = platform.system()
_TARGET_OS = ''
_ARCH = ''
_PREFIX = ''
_BIN_EXT = ''
_ARCHIVE_EXT = ''
if _PLATFORM == 'Windows':
    _BIN_EXT = '.dll'
    _ARCHIVE_EXT = '.zip'
    _TARGET_OS = 'win'
    _ARCH = 'x64' if platform.machine().endswith('64') else 'x86'
elif _PLATFORM == 'Darwin':
    _PREFIX = 'lib'
    _BIN_EXT = '.dylib'
    _ARCHIVE_EXT = '.tar.gz'
    _TARGET_OS = 'macos'
    _ARCH = 'universal'
elif _PLATFORM == 'Linux':
    _PREFIX = 'lib'
    _BIN_EXT = '.so'
    _ARCHIVE_EXT = '.tar.gz'
    _TARGET_OS = 'linux'
    if platform.machine().startswith('aarch64'):
        _ARCH = 'arm64'
    elif platform.machine().startswith('arm64'):
        _ARCH = 'arm64'
    elif platform.machine().startswith('arm'):
        _ARCH = 'arm32'
    elif platform.machine().endswith('64'):
        _ARCH = 'x64'
    else:
        raise ImportError('Cannot identify CPU architecture')
else:
    raise ImportError('Not supported OS')

_LIB_NAME_ORIGIN_BASE = f'{_PREFIX}autd3capi'
_LIB_NAME_BASE = f'{_PREFIX}autd3capi_{_VERSION_TRIPLE}'
_LIB_PATH = os.path.join(os.path.dirname(__file__), 'bin')
_LIB_NAMES = [f'{_BIN_EXT}', f'-holo-gain{_BIN_EXT}', f'-soem-link{_BIN_EXT}', f'-twincat-link{_BIN_EXT}']


def download_bin():
    asset_base_url = 'https://github.com/shinolab/autd3-library-software/releases/download/'
    version = f'v{_VERSION_TRIPLE}'

    url = f'{asset_base_url}{version}/autd3-{version}-{_TARGET_OS}-{_ARCH}{_ARCHIVE_EXT}'

    module_path = os.path.dirname(__file__)
    tmp_archive_path = os.path.join(module_path, 'tmp' + _ARCHIVE_EXT)

    res = requests.get(url, stream=True)
    with open(tmp_archive_path, 'wb') as fp:
        shutil.copyfileobj(res.raw, fp)

    if _ARCHIVE_EXT == '.zip':
        with zipfile.ZipFile(tmp_archive_path) as f:
            for info in f.infolist():
                if info.filename.startswith('bin') and info.filename.endswith(_BIN_EXT):
                    f.extract(info, module_path)
    elif _ARCHIVE_EXT == '.tar.gz':
        with tarfile.open(tmp_archive_path) as f:
            libraries = []
            for i in f.getmembers():
                if i.name.startswith('bin') and i.name.endswith(_BIN_EXT):
                    libraries.append(i)
            f.extractall(path=module_path, members=libraries)

    os.remove(tmp_archive_path)


def load_latest_binary():
    exists_all = True
    for name in _LIB_NAMES:
        exists_all = exists_all & os.path.exists(os.path.join(_LIB_PATH, _LIB_NAME_BASE + name))

    if exists_all:
        return

    print('Cannot find latest binaries. Downloading latest binaries...')

    for file in glob.glob(os.path.join(os.path.dirname(__file__), 'bin', '*')):
        if file.endswith(_BIN_EXT):
            try:
                os.remove(file)
            except Exception:
                print(f'Warning: cannot delete old binary ({file})')

    download_bin()

    for file in glob.glob(os.path.join(os.path.dirname(__file__), 'bin', '*')):
        if file.endswith(_BIN_EXT):
            os.rename(file, file.replace(_LIB_NAME_ORIGIN_BASE, _LIB_NAME_BASE))
    print('Done')


load_latest_binary()
Nativemethods().init_dll(_LIB_PATH, _PREFIX, _BIN_EXT)
Nativemethods().init_autd3capi()
Nativemethods().init_autd3capi_holo_gain()
Nativemethods().init_autd3capi_twincat_link()
if _PLATFORM == 'Windows':
    Nativemethods().init_autd3capi_emulator_link()
