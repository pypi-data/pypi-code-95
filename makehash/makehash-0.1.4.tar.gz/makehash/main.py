# -*- coding: utf-8 -*-
#
# Copyright (c) 2020~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from typing import *
import os
import sys
import traceback
import re

import click
from click_anno import click_app
from click_anno.types import flag
from fsoopify import NodeInfo, NodeType, FileInfo, DirectoryInfo, SerializeError
from alive_progress import alive_bar

EXTENSION_NAME = '.hash'
ACCEPT_HASH_TYPES = ('sha1', 'md5', 'crc32', 'sha256')

class IHashAccessor:
    def can_read(self, f: FileInfo) -> bool:
        raise NotImplementedError

    def read(self, f: FileInfo) -> Optional[Dict[str, str]]:
        raise NotImplementedError

    def write(self, f: FileInfo, h: Dict[str, str]):
        raise NotImplementedError

class HashFileHashAccessor(IHashAccessor):
    @staticmethod
    def _get_checksum_file(f: FileInfo):
        return FileInfo(f.path + EXTENSION_NAME)

    def can_read(self, f: FileInfo) -> bool:
        return self._get_checksum_file(f).is_file()

    def read(self, f: FileInfo) -> Optional[Dict[str, str]]:
        hash_file = self._get_checksum_file(f)
        try:
            data = hash_file.load('json')
        except (SerializeError, IOError):
            return None
        else:
            if isinstance(data, dict):
                return data
            return None

    def write(self, f: FileInfo, h: Dict[str, str]):
        hash_file = self._get_checksum_file(f)
        hash_file.dump(h, 'json')


class Crc32SuffixHashAccessor(IHashAccessor):
    REGEX = re.compile(r'\((?P<crc32>[0-9a-f]{8})\)$', re.I)

    @classmethod
    def _try_read_crc32(cls, f: FileInfo) -> Optional[str]:
        pure_name = str(f.path.name.pure_name)
        match = cls.REGEX.search(pure_name)
        if match:
            return match.group('crc32')

    def can_read(self, f: FileInfo) -> bool:
        return self._try_read_crc32(f)

    def read(self, f: FileInfo) -> Optional[Dict[str, str]]:
        crc32 = self._try_read_crc32(f)
        return dict(crc32=crc32)

    def write(self, f: FileInfo, h: Dict[str, str]):
        raise NotImplementedError


def _get_hash_value(f: FileInfo, hash_names: List[str]) -> Dict[str, str]:
    r = {}
    with f.get_hasher(*hash_names) as hasher:
        with alive_bar(manual=True) as bar:
            while hasher.read_block():
                bar(hasher.progress)
        for name, val in zip(hash_names, hasher.result):
            r[name] = val
    return r

def _norm_hashvalue(val):
    if isinstance(val, str):
        return val.lower()
    return None

def verify_file(f: FileInfo, accessor: Optional[IHashAccessor]):
    if accessor is None:
        def iter_accessors():
            yield HashFileHashAccessor()
            yield Crc32SuffixHashAccessor()
        accessors = iter_accessors()
    else:
        accessors = (accessor, )

    data = None
    for accessor in accessors:
        data = accessor.read(f)
        if data is not None:
            break
    if data is None:
        if f.path.name.ext != EXTENSION_NAME:
            click.echo('Ignore {} by checksum not found.'.format(
                click.style(str(f.path), fg='blue')
            ))
        return

    # find hash type:
    hash_names = []
    saved_hash_value = {}
    for hash_name in ACCEPT_HASH_TYPES:
        if hash_name in data:
            hash_names.append(hash_name)
            saved_hash_value[hash_name] = _norm_hashvalue(data[hash_name])

    if not hash_names:
        click.echo('Ignore {} by no known algorithms.'.format(
            click.style(str(f.path), fg='blue')
        ))
        return

    click.echo('Verifing {}... '.format(
        click.style(str(f.path), fg='blue')
    ))
    actual_hash_value = _get_hash_value(f, hash_names)
    click.echo('Result : ', nl=False)
    if actual_hash_value == saved_hash_value:
        click.echo(click.style("Ok", fg="green") + '.')
    else:
        click.echo(click.style("Failed", fg="red") + '!')

def create_checksum_file(f: FileInfo, skip_exists: bool, accessor: IHashAccessor):
    if skip_exists and accessor.can_read(f):
        click.echo('Skiped {} by checksum exists.'.format(
            click.style(str(f.path), fg='bright_blue')
        ), nl=True)
        return

    hash_name = ACCEPT_HASH_TYPES[0]
    click.echo('Computing checksum for {}...'.format(
            click.style(str(f.path), fg='bright_blue')
        ), nl=True)

    hash_values = _get_hash_value(f, [hash_name])
    data = {}
    data[hash_name] = hash_values[hash_name]
    accessor.write(f, data)

def _collect_files(paths: list, skip_hash_file: bool) -> List[FileInfo]:
    '''
    collect a files list
    '''

    collected_files: List[FileInfo] = []

    def collect_from_dir(d: DirectoryInfo):
        for item in d.list_items():
            if item.node_type == NodeType.file:
                collected_files.append(item)
            elif item.node_type == NodeType.dir:
                collect_from_dir(item)

    if paths:
        for path in paths:
            node = NodeInfo.from_path(path)
            if node is not None:
                if node.node_type == NodeType.file:
                    collected_files.append(node)
                elif node.node_type == NodeType.dir:
                    collect_from_dir(node)
            else:
                click.echo(f'Ignore {path} which is not a file or dir')

        # ignore *.hash file
        if skip_hash_file:
            collected_files = [f for f in collected_files if f.path.name.ext != EXTENSION_NAME]

        if collected_files:
            click.echo('Found {} files.'.format(
                click.style(str(len(collected_files)), fg='bright_blue')
            ))
        else:
            click.echo(click.style("Path is required", fg="yellow"))
    else:
        click.echo(click.style("Path is required", fg="red"))

    return collected_files

def make_hash(*paths, skip_exists: flag=True, skip_hash_file: flag=True):
    'create *.hash files'
    collected_files = _collect_files(paths, skip_hash_file)
    accessor = HashFileHashAccessor()
    if collected_files:
        for f in collected_files:
            create_checksum_file(f, skip_exists=skip_exists, accessor=accessor)

def verify_hash(*paths, skip_hash_file: flag=True):
    'verify with *.hash files'
    collected_files = _collect_files(paths, skip_hash_file)
    accessor = None # HashFileHashAccessor()
    if collected_files:
        for f in collected_files:
            verify_file(f, accessor=accessor)

@click_app
class App:
    def make(self, *paths, skip_exists: flag=True, skip_hash_file: flag=True):
        'create *.hash files'
        make_hash(*paths, skip_exists, skip_hash_file)

    def verify(self, *paths, skip_hash_file: flag=True):
        'verify with *.hash files'
        verify_hash(*paths, skip_hash_file)

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        App()(argv[1:])
    except Exception: # pylint: disable=W0703
        traceback.print_exc()

if __name__ == '__main__':
    main()
