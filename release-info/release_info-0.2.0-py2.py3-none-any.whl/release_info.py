# coding: utf-8

import sys
import os
from pathlib import Path
import datetime
import subprocess
from configparser import ConfigParser
import urllib.request

import hashlib
import tarfile


from _ast import *  # NOQA
from ast import parse  # NOQA

if sys.version_info >= (3, 8):
    from ast import Str, Num, Bytes, NameConstant  # NOQA

from .__init__ import version_info  # NOQA


class ReleaseInfo:
    def __init__(self, args=None, config=None):
        self._args = args
        self.verbose = 0 if args is None else self._args.verbose
        self._config = None
        self._config_name = 'config.ini'
        self._config_dir = None
        self._data = None

    @property
    def config(self):
        """read config file, create template if not available"""
        if self._config is not None:
            return self._config
        cp = self.config_path.expanduser()
        if not cp.exists():
            cp.write_text(_CONFIG_TEMPLATE)
        self._config = ConfigParser()
        self._config.read(cp)
        return self._config

    @property
    def config_path(self):
        # this is usually unexpanded
        return self.config_dir / self._config_name

    @config_path.setter
    def config_path(self, p):
        p = Path(p)
        if not p.expanduser().exists():
            print('config_path', p, 'does not exist')
            sys.exit(1)
        self._config_name = p.name
        self._config_dir = p.parent

    @property
    def config_dir(self):
        if self._config_dir:
            return self._config_dir
        if sys.platform.startswith('win32'):
            d = Path(os.environ['APPDATA'])
        else:
            d = Path(os.environ.get('XDG_CONFIG_HOME', '~/.config'))
        d /= 'python_release_info'
        d.expanduser().mkdir(parents=True, exist_ok=True)
        self._config_dir = d
        return d

    @property
    def data_path(self):
        return self.config_dir.expanduser() / 'release_info.pon'

    @property
    def data(self):
        if self._data is None:
            self._data = self.eval_s(self.data_path.read_text())
        return self._data

    def eval_s(self, s):
        res = _literal_eval(s)
        nv = res.get('util_version', (0, 0))
        if nv > version_info:
            if nv[0] == version_info[0]:
                print(f'a newer version ({nv} > {version_info} is '
                      'available please update')
            else:
                print(
                    f'a newer major version ({nv} > {version_info} '
                    'is available you have to update'
                )
        for key, ow in (('add', False), ('overwrite', True)):
            try:
                add_path = self.config['INFO'][key]
            except KeyError:
                add_path = None
            if add_path is not None:
                if os.path.sep not in add_path:
                    add_path = self.config_dir.expanduser() / add_path
                else:
                    add_path = Path(add_path).expanduser()
                d = _literal_eval(add_path.read_text())
                update_data(res, d, overwrite=ow)
        return res

    def check(self, type=None, args=None):
        """check loaded pon files (release_info.pon and add/overwrite file from config.ini"""
        if type is None:
            type = 'cpython' if args is None or args.type is None else args.type
        last = (0, 0)
        for major_minor, data in self.data[type].items():
            assert len(major_minor) == 2
            assert major_minor > last
            last = major_minor
            prev_date = datetime.date(1900, 1, 1)
            for _k, v in data.items():
                if not isinstance(v, dict):
                    continue
                rel_date = v.get('rel', None)
                if rel_date is not None:
                    # print(k, rel_date, prev_date)
                    assert rel_date >= prev_date
                    prev_date = rel_date
        print('check: ok')

    def find_current(self, type=None, dd=None, pre=False):
        """return highest (major, minor, micro) for non-eol major/minor version
        pre: False -> skip , None -> include, True -> only: pre-release information
        """
        if type is None:
            type = 'cpython'
        if dd is None:
            dd = datetime.date.today()
        for major_minor, data in self.data[type].items():
            mmm = (major_minor[0], major_minor[1], -1)
            eol = None
            for k, v in data.items():
                if k == 'eol':
                    eol = v
                if isinstance(k, tuple):
                    if v['rel'] > dd:
                        continue
                    try:
                        if k > mmm:
                            mmm = k
                    except TypeError:
                        # can be None,  there was e.g. never a 2.6.0 and
                        # 2.6 is  coded as (2, 6, None)
                        mmm = k
            else:
                if eol is None:
                    continue
                if eol is True:
                    eol = data[mmm]['rel']  # take eol date from last release
                if not isinstance(eol, datetime.date):
                    print(f'{eol=}', major_minor) 
                if len(mmm) == 3:
                    if pre is True:
                        continue
                else:
                    if pre is False:
                        continue
                if eol > dd and mmm[2] != -1:
                    yield mmm

    def released_after(self, dd, type=None, pre=False):
        res = []
        if type is None:
            type = 'cpython'
        for major_minor, data in self.data[type].items():
            # mmm = (major_minor[0], major_minor[1], -1)
            for k, v in data.items():
                if k == 'eol':
                    break
                if isinstance(k, tuple):
                    if not isinstance(v['rel'], datetime.date):
                        print('date?', repr(v['rel']))
                        continue
                    if v['rel'] <= dd:
                        continue
                    if len(k) == 3:
                        if pre is True:
                            continue
                    else:
                        if pre is False:
                            continue
                    res.append(k)
        return res

    def print_current(self, type=None, dd=None, args=None, pre=False):
        if args is None:
            args = self._args
        if type is None:
            type = 'cpython' if args is None or args.type is None else args.type
        if dd is None:
            dd = (
                datetime.date.today()
                if args is None or args.dd is None
                else datetime.date.strptime(args.dd.replace('-', ''), '%Y%m%d')
            )
        for v in self.find_current(type=type, dd=dd, pre=pre):
            print('.'.join((str(s) for s in v)))

    def print_pre(self, type=None, dd=None):
        self.print_current(type=type, dd=dd, args=self._args, pre=True)

    def release_date(self, version, type='cpython'):
        data = self.data[type][version[0:2]][version]
        return data['rel']

    def src_url(self, version, type='cpython'):
        # >= 2011-02-20 -> tar.xz
        # >= 2003-10-03 -> tar.bz2
        rd = self.release_date(version)
        if rd >= datetime.date(2011, 2, 20):
            ext = 'tar.xz'
        elif rd >= datetime.date(2003, 10, 3):
            ext = 'tar.bz2'
        else:
            ext = '.tgz'
        svb = '.'.join([str(d) for d in version[:3]])
        sv = '.'.join(
            [str(version[0]), str(version[1]), "".join((str(d) for d in version[2:]))]
        )
        return f'https://www.python.org/ftp/python/{svb}/Python-{sv}.{ext}'

    @staticmethod
    def vertupstr(version):
        return '.'.join([str(version[0]), str(version[1]), "".join((str(d) for d in version[2:]))])

    def src_md5(self, version, type='cpython'):
        data = self.data[type][version[0:2]][version]
        return data.get('md5', None)

    @staticmethod
    def split_version(vs):
        version = []
        for x in vs.split('.'):
            try:
                ix = int(x)
                version.append(ix)
            except ValueError:
                while x:
                    d = ""
                    if x[0].isdigit():
                        while x and x[0].isdigit():
                            d += x[0]
                            x = x[1:]
                        version.append(int(d))
                        d = ""
                    else:
                        while x and not x[0].isdigit():
                            d += x[0]
                            x = x[1:]
                        version.append(d)
                        d = ""
        return tuple(version)

    def download(self, version=None, dir=None, type=None, extract=None, force=None):
        if version is None:
            print('args', self._args)
            if self._args is None or self._args.version is None:
                print('need to specify version to download')
            if self._args is None:
                return 1
            version = self.split_version(self._args.version)
        if type is None:
            type = 'cpython' if self._args is None or self._args.type is None else self._args.type
        if dir is None:
            dir = '.' if self._args is None or self._args.dir is None else self._args.dir
        if extract is None:
            extract = self._args.extract if self._args is not None else False
        if force is None:
            force = self._args.force if self._args is not None else False
        url = self.src_url(version, type=type)
        path = Path(dir) / url.rsplit('/', 1)[1]
        if not path.exists() or force:
            md5 = self.src_md5(version)
            with urllib.request.urlopen(url) as response:
                with path.open('wb') as fp:
                    if md5:
                        fh = hashlib.md5()
                    # 3.8 -> while chunk := response.read(16384)
                    chunk = response.read(16384)
                    while chunk:
                        if md5:
                            fh.update(chunk)
                        fp.write(chunk)
                        chunk = response.read(16384)
                if md5 and fh.hexdigest() != md5:
                    print("md5sum doesn't match for {path}")
        elif self.verbose > 0:
            print(f'version {version} already downloaded')
        if extract:  # extract what is on disk, not as efficient as direct from download...
            extr_dir = Path(str(path).rsplit('.tar', 1)[0])
            if not extr_dir.exists() or force:
                tf = tarfile.open(path, 'r:*')
                tf.extractall(path=path.parent)
            elif self.verbose > 0:
                print(f'version {version} already extracted')

    def download_data(self, dir=None, extract=False, delay=0, force=False, bldcmd=None):
        if extract and dir is None:
            print('need to specify dir (for download) when extracting')
            return
        if bldcmd is not None and not extract:
            print('need to extract when giving build command')
            return
        delay = datetime.timedelta(days=delay if delay else 0)
        try:
            old_date = self.data['dd']
        except KeyError:
            old_date = datetime.date(2020, 1, 1)
        url = 'https://sourceforge.net/p/release-info/code/ci/default/tree/' \
            'release_info.pon?format=raw'
        dp = self.data_path.expanduser()
        tmp_file = dp.with_suffix('.pon.new')
        with urllib.request.urlopen(url) as response:
            with tmp_file.open('wb') as fp:
                chunk = response.read(16384)
                while chunk:
                    fp.write(chunk)
                    chunk = response.read(16384)
        self._data = x = self.eval_s(tmp_file.read_text())
        if self.verbose > 0:
            print(self.data.get('dd', old_date) , old_date, old_date + delay)
        new_rels = self.released_after(old_date)
        for x in new_rels:
            print(self.vertupstr(x))
        self.data_path.unlink(missing_ok=True)
        tmp_file.rename(self.data_path)
        if self.data.get('dd') < old_date + delay:
            print('delaying update until', old_date + delay)
            return 0
        if self.data.get('dd', old_date) <= old_date:
            return 1
        # download if dir specified, extract if appropriate
        for v in new_rels:
            self.download(version=v, dir=dir, type='cpython', extract=extract,
                          force=force)
        # run command in extraction directory
        res = new_rels
        if bldcmd:
            for v in new_rels:
                if self.build(v, dir, bldcmd):
                    res = 2
        return res

    def build(self, version, dir, bldcmd):
        """change to extracted version dir and build"""
        curdir = os.getcwd()
        try:
            v = self.vertupstr(version)
            os.chdir(Path(dir) / ('Python-' + v))
            os.environ['PYTHONVERSION'] = v
            print('curdir', os.getcwd())
            print('cmd:', repr(bldcmd))
            sys.stdout.flush()
            # os.system(bldcmd)
            res = subprocess.run(bldcmd,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 shell=True)
            print('res', res)
        except Exception as e:
            print('exception thrown', e)
            return 1
        os.chdir(curdir)
        return res.returncode

    def update(self):
        res = self.download_data(dir=self._args.dir, extract=self._args.extract,
                                  delay=self._args.delay,
                                  force=self._args.force, bldcmd=self._args.build)
        if not isinstance(res, int):
            res = 0
        return res

    def current(self):
        return self.print_current()

    def pre(self):
        return self.print_pre()


release_info = ReleaseInfo()

_CONFIG_TEMPLATE = """\
[INFO]
# you can add to, or overwrite, the default release info in release_info.pon by
# specifying files here. If the filename has no dir seperator, it is assumed to "live"
# next to release_info.pon use add for information missing in release_info.pon,
# use overwrite for information that is incorrect or missing in release_info.pon
#add =
#overwrite =
"""


if sys.version_info < (3,):
    string_type = basestring
else:
    string_type = str


def _literal_eval(node_or_string):
    """
    Safely evaluate an expression node or a string containing a Python
    expression.  The string or node provided may only consist of the following
    Python literal structures: strings, bytes, numbers, tuples, lists, dicts,
    sets, booleans, integer, float, date, datetime, and None.
    You can use add/substract on nodes.
    """
    _safe_names = {'None': None, 'True': True, 'False': False}
    if isinstance(node_or_string, string_type):
        node_or_string = parse(node_or_string, mode='eval')
    if isinstance(node_or_string, Expression):
        node_or_string = node_or_string.body
    else:
        raise TypeError('only string or AST nodes supported')

    def _convert(node):
        if isinstance(node, Str):
            if sys.version_info < (3,) and not isinstance(node.s, unicode):
                return node.s.decode('utf-8')
            return node.s
        elif isinstance(node, Bytes):
            return node.s
        elif isinstance(node, Num):
            return node.n
        elif isinstance(node, Tuple):
            return tuple(map(_convert, node.elts))
        elif isinstance(node, List):
            return list(map(_convert, node.elts))
        elif isinstance(node, Set):
            return set(map(_convert, node.elts))
        elif isinstance(node, Dict):
            return dict((_convert(k), _convert(v)) for k, v in zip(node.keys, node.values))
        elif isinstance(node, NameConstant):
            return node.value
        elif sys.version_info < (3, 4) and isinstance(node, Name):
            if node.id in _safe_names:
                return _safe_names[node.id]
        elif (
            isinstance(node, UnaryOp)
            and isinstance(node.op, (UAdd, USub))
            and isinstance(node.operand, (Num, UnaryOp, BinOp))
        ):  # NOQA
            operand = _convert(node.operand)
            if isinstance(node.op, UAdd):
                return +operand
            else:
                return -operand
        elif (
            isinstance(node, BinOp)
            and isinstance(node.op, (Add, Sub))
            and isinstance(node.right, (Num, UnaryOp, BinOp))
            and isinstance(node.left, (Num, UnaryOp, BinOp))
        ):  # NOQA
            left = _convert(node.left)
            right = _convert(node.right)
            if isinstance(node.op, Add):
                return left + right
            else:
                return left - right
        elif isinstance(node, Call):
            func_id = getattr(node.func, 'id', None)
            if func_id == 'dict':
                return dict((k.arg, _convert(k.value)) for k in node.keywords)
            elif func_id == 'set':
                return set(_convert(node.args[0]))
            elif func_id == 'date':
                return datetime.date(*[_convert(k) for k in node.args])
            elif func_id == 'datetime':
                return datetime.datetime(*[_convert(k) for k in node.args])
        err = SyntaxError('malformed node or string: ' + repr(node))
        err.filename = '<string>'
        err.lineno = node.lineno
        err.offset = node.col_offset
        err.text = repr(node)
        err.node = node
        raise err

    return _convert(node_or_string)


def update_data(d1, d2, overwrite=False):
    """add data to d1 from d2, if overwrite is False, only add new leaf nodes not yet in d1"""
    if isinstance(d2, dict):
        for k in d2:
            if k not in d1:
                d1[k] = d2[k]
            else:
                if isinstance(d2[k], (dict, list)):
                    update_data(d1[k], d2[k], overwrite=overwrite)
                elif overwrite:
                    d1[k] = d2[k]
    elif isinstance(d2, list):  # only works for updating dict/list children in a list
        for idx, _e in d2:
            if isinstance(d2[k], (dict, list)):
                update_data(d1[idx], d2[idx], overwrite)
