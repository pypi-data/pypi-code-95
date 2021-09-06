import os
from re import match
from sys import version_info
from os import remove

if version_info[0] == 3 and version_info[1] <= 4:
    from scandir import scandir
else:
    from os import scandir
from os import path as os_path, sep
from platform import node
from sqlite3 import connect, OperationalError, Row
from logging import info, basicConfig, INFO, error, warning
from pathlib import Path
from conffu import Config


# noinspection SqlResolve
class TreeWalker:
    log_freq = 1000
    lines = 0
    node = node()

    def rewrite_path(self, p):
        p = str(Path(p).resolve())
        return r'\\{}\{}${}'.format(self.node, p[0].lower(), p[2:]) \
            if self.rewrite_admin and len(p) > 1 and p[1] == ':' else p

    def __init__(self, fn, overwrite=False, rewrite=True, rewrite_admin=True, override=False):
        existed = Path(fn).is_file()
        if existed and overwrite:
            remove(fn)

        self._fn = fn
        self._conn = connect(fn)
        self.c = self._conn.cursor()

        self.c.execute('DROP TABLE IF EXISTS old_dirs')
        self.c.execute('DROP TABLE IF EXISTS old_files')
        self.c.execute('DROP TABLE IF EXISTS old_no_access')

        self.rewrite = rewrite
        self.rewrite_admin = rewrite_admin
        self.options = ['rewrite', 'rewrite_admin']

        def set_options():
            self.c.execute('CREATE TABLE options (key text, value text)')
            for key in self.options:
                self.c.execute('INSERT INTO options VALUES(?, ?)', (key, self.__getattribute__(key)))

        def get_options():
            for key in self.options:
                value = self.c.execute('SELECT value FROM options WHERE key=?', [key]).fetchone()[0]
                option = self.__getattribute__(key)
                if value is None:
                    self.c.execute('INSERT INTO options VALUES(?, ?)', (key, option))
                else:
                    if option != type(option)(value):
                        if override:
                            self.c.execute('UPDATE options SET value = ? WHERE key = ?', (option, key))
                        error('options for database do not match, \'{}\' is {}', key, option)

        if not existed or overwrite:
            set_options()
            self.c.execute('CREATE TABLE no_access (id int, parent_dir int, name text, problem int)')
            self.c.execute('CREATE TABLE dirs (id int, parent_dir int, name text, size int, total_file_count int, '
                           'file_count int, min_mtime int, min_atime int)')
            self.c.execute('CREATE TABLE files (parent_dir int, name text, size int, mtime int, atime int)')
            self.next_dir_id = 0
        else:
            if self.c.execute(
                    'SELECT name FROM sqlite_master WHERE type="table" AND name="options"').fetchone() is None:
                set_options()
            else:
                get_options()

            self.c.execute('SELECT MAX(id) FROM dirs')
            x = self.c.fetchone()[0]
            self.next_dir_id = 0 if x is None else x + 1

    @property
    def fn(self):
        return self._fn

    @classmethod
    def log_loop(cls, *args):
        if cls.lines % cls.log_freq == 0:
            info(*args)
        cls.lines += 1

    def _do_walk(self, path, parent_dir=-1, filter_callback=None):
        self.__class__.log_freq = 100
        dir_id = self.next_dir_id
        self.next_dir_id += 1
        self.log_loop('Processing {}, {}'.format(path, dir_id))
        total_size, min_mtime, min_atime, total_count, count, size = 0, 10000000000, 10000000000, 0, 0, 0
        try:
            for entry in scandir(path):
                if filter_callback is None or filter_callback(entry.name):
                    # inspection required due to PyCharm issue PY-46041
                    # noinspection PyUnresolvedReferences
                    if entry.is_dir(follow_symlinks=False):
                        # noinspection PyUnresolvedReferences
                        size, sub_count, mtime, atime = self._do_walk(entry.path, dir_id)
                        total_count += sub_count
                    else:
                        # noinspection PyUnresolvedReferences
                        stat = entry.stat(follow_symlinks=False)
                        size = stat.st_size
                        mtime = int(stat.st_mtime)
                        atime = int(stat.st_atime)
                        total_count += 1
                        count += 1
                        # noinspection PyUnresolvedReferences
                        self.c.execute('INSERT INTO files VALUES(?, ?, ?, ?, ?)',
                                       [dir_id, entry.name, size, mtime, atime])
                    total_size += size
                    min_mtime = min(min_mtime, mtime)
                    min_atime = min(min_atime, atime)
        except PermissionError:
            print('Permission error trying to process: {}'.format(path))
            self.c.execute('INSERT INTO no_access VALUES(?, ?, ?, 0)',
                           [dir_id, parent_dir, path])
        except FileNotFoundError:
            print('File not found error trying to process: {}'.format(path))
            print(os.getcwd())
            self.c.execute('INSERT INTO no_access VALUES(?, ?, ?, 1)',
                           [dir_id, parent_dir, path])

        self.c.execute('INSERT INTO dirs VALUES(?, ?, ?, ?, ?, ?, ?, ?)',
                       [dir_id, parent_dir, path, total_size, total_count, count, min_mtime, min_atime])
        return total_size, total_count, min_mtime, min_atime

    def walk(self, path, parent_dir=-1, filter_callback=None):
        if self.rewrite:
            path = self.rewrite_path(path)
        return self._do_walk(path, parent_dir, filter_callback)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.commit()
        self.close()

    def commit(self):
        try:
            self.c.execute('COMMIT')
        except OperationalError as e:
            if not str(e).endswith('no transaction is active'):
                raise e

    def close(self):
        self._conn.close()

    def add_db(self, fn):
        def do_add(dir_id, parent_dir):
            nonlocal ca
            ca.execute('SELECT * FROM dirs WHERE id = ?', [dir_id])
            self.c.execute('INSERT INTO dirs VALUES(?, ?, ?, ?, ?, ?, ?, ?)',
                           (self.next_dir_id, parent_dir) + ca.fetchone()[2:])
            ca.execute('SELECT * FROM files WHERE parent_dir = ?', [dir_id])
            for f in ca.fetchall():
                self.c.execute('INSERT INTO files VALUES(?, ?, ?, ?, ?)',
                               (self.next_dir_id,) + f[1:])
            ca.execute('SELECT id FROM dirs WHERE parent_dir = ?', [dir_id])
            new_dir_id = self.next_dir_id
            self.next_dir_id += 1
            for d in ca.fetchall():
                do_add(d[0], new_dir_id)

        conn_add = connect(fn)
        try:
            ca = conn_add.cursor()
            ca.execute('SELECT name, id FROM dirs WHERE parent_dir = -1')
            for r in ca.fetchall():
                self.remove(r[0])
                do_add(r[1], -1)
        finally:
            conn_add.close()

    def merge(self, fn):
        self.next_dir_id = self._do_reindex(connect(fn), offset=self.next_dir_id)

        self.c.execute('ATTACH DATABASE "{}" AS adding'.format(fn))
        self.c.execute('INSERT INTO dirs SELECT * FROM adding.dirs')
        self.c.execute('INSERT INTO files SELECT * FROM adding.files')
        self.c.execute('INSERT INTO no_access SELECT * FROM adding.no_access')
        self.c.execute('COMMIT')
        self.c.execute('DETACH DATABASE adding')

    @staticmethod
    def _do_reindex(connection, offset=0):
        cursor = connection.cursor()
        mapping = {old_key: new_key + offset for new_key, old_key in
                   enumerate(
                       t[0]
                       for t in cursor.execute(
                           'SELECT id FROM dirs ORDER BY id'
                       ).fetchall()
                   )
                   } | {-1: -1}

        cursor.execute('ALTER TABLE dirs RENAME TO old_dirs')
        cursor.execute('CREATE TABLE dirs (id int, parent_dir int, name text, size int, total_file_count int, '
                       'file_count int, min_mtime int, min_atime int)')
        # separate cursor for reading, reusing self.c in loop
        data = connection.execute('SELECT * FROM old_dirs')
        for row in data:
            cursor.execute('INSERT INTO dirs VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                           [mapping[row[0]], mapping[row[1]]] + list(row[2:]))
        cursor.execute('DROP TABLE old_dirs')

        cursor.execute('ALTER TABLE files RENAME TO old_files')
        cursor.execute('CREATE TABLE files (parent_dir int, name text, size int, mtime int, atime int)')
        # separate cursor for reading, reusing self.c in loop
        data = connection.execute('SELECT * FROM old_files')
        for row in data:
            cursor.execute('INSERT INTO files VALUES (?, ?, ?, ?, ?)',
                           [mapping[row[0]]] + list(row[1:]))
        cursor.execute('DROP TABLE old_files')

        cursor.execute('ALTER TABLE no_access RENAME TO old_no_access')
        cursor.execute('CREATE TABLE no_access (id int, parent_dir int, name text, problem int)')
        # separate cursor for reading, reusing self.c in loop
        data = connection.execute('SELECT * FROM old_no_access')
        for row in data:
            cursor.execute('INSERT INTO no_access VALUES (?, ?, ?, ?)',
                           [mapping[row[0]], mapping[row[1]]] + list(row[2:]))
        cursor.execute('DROP TABLE old_no_access')
        cursor.execute('COMMIT')

        next_id = cursor.execute('SELECT MAX(id) FROM dirs').fetchone()[0]
        return 0 if next_id is None else next_id + 1

    def reindex(self):
        self._do_reindex(self._conn)

    @staticmethod
    def _is_relative(p1, p2):
        """
        Returns if p1 is relative to p2, i.e. if p1 is either the same as p2, or a sub-directory of p2
        :param p1: path
        :param p2: path
        :return: bool, whether p1 is relative to p2
        """
        # instead of Path.is_relative_to, to ensure 3.4.4 compatibility
        rp1, rp2 = os_path.realpath(p1), os_path.realpath(p2)
        return rp1.startswith(rp2) and (len(rp1) == len(rp2) or rp1[len(rp2)] == sep)

    def remove(self, p):
        def do_remove(dir_id):
            def _query(table, key):
                self.c.execute('DELETE FROM {} '
                               'WHERE {} IN ('
                               '  WITH RECURSIVE children(dir) AS ('
                               '    SELECT ? '
                               '    UNION ALL '
                               '    SELECT dirs.id FROM dirs, children WHERE dirs.parent_dir = children.dir'
                               '  ) '
                               'SELECT dir FROM children)'.format(table, key), [dir_id])
            _query('no_access', 'parent_dir')
            _query('files', 'parent_dir')
            _query('dirs', 'id')

        if self.rewrite:
            p = self.rewrite_path(p)
        self.c.execute('SELECT name, id FROM dirs WHERE parent_dir = -1')
        for r in self.c.fetchall():
            # if a 'root' directory (i.e. without parent) falls within p, remove it (and its children)
            if self._is_relative(r[0], p):
                do_remove(r[1])
            # if p falls within a 'root' directory find that record for p and remove it (and its children)
            elif self._is_relative(p, r[0]):
                self.c.execute('SELECT id FROM dirs WHERE name = ?', [p])
                _id = self.c.fetchone()[0]
                if _id is None:
                    warning('Attempting to remove "{p}" from within "{r[0]}", but no longer in database')
                do_remove(_id)

    def update(self, p, remove_old=True):
        if self.rewrite:
            p = self.rewrite_path(p)
        if remove_old:
            self.remove(p)
        self._do_walk(p)

    def get_tree(self, p=None, d=None):
        if d is None:
            if p is None:
                self.c.execute('SELECT name, id FROM dirs WHERE parent_dir = -1')
                return {r[0]: self.get_tree(d=r[1]) for r in self.c.fetchall()}
            self.c.execute('SELECT id FROM dirs WHERE name = ?', [p])
            d = self.c.fetchone()[0]
        if d is None:
            return False
        self.c.execute('SELECT name, id FROM dirs WHERE parent_dir = ?', [d])
        result = {Path(r[0]).name: self.get_tree(d=r[1]) for r in self.c.fetchall()}
        self.c.execute('SELECT name FROM files WHERE parent_dir = ?', [d])
        return result | {r[0]: None for r in self.c.fetchall()}

    def _get_list(self, p, files=True):
        rf = self._conn.row_factory
        try:
            self._conn.row_factory = Row
            if self.rewrite:
                p = self.rewrite_path(p)
            self.c.execute(
                'SELECT l.name, l.size, l.{0}mtime, l.{0}atime '
                'FROM {1} AS l JOIN dirs ON dirs.id = l.parent_dir '
                'WHERE dirs.name = ?'.format(('' if files else 'min_'), ('files' if files else 'dirs')), [p])
            return self.c.fetchall()
        finally:
            self._conn.row_factory = rf

    def get_files(self, p):
        return self._get_list(p, True)

    def get_dirs(self, p):
        return self._get_list(p, False)


def cli_entry_point():
    main()


def print_help():
    print(
        'Treewalker traverses a directory tree from a starting path, adding files and folders to a SQLite3 database.\n'
        '\n'
        'Usage: `treewalker [options] --output filename --walk path(s) | --merge filename\n'
        '\n'
        'Options:\n'
        '-h/--help                     : This text.\n'
        '-o/--output filename          : Filename for the SQLite3 database to write to. (required)\n'
        '-w/--walk path [path [..]]    : Path(s) to `walk` and add to the database.\n'
        '-m/--merge filename           : Filename of a 2nd database to merge into output.\n'
        '-rm/--remove path [path [..]] : Path(s) to recursively remove from the database.\n'
        '                                (--path, --merge or --remove required)\n'
        '-ow/--overwrite               : Overwrite (wipe) the output database (or to add to it). (default False)\n'
        '-rw/--rewrite                 : Rewrite paths to resolved paths. (default True, set to False or 0 to change)\n'
        '-ra/--rewrite_admin           : Rewrite local drive letters to administrative shares. (default True)\n'
        '\n'
        'Examples:\n'
        '\n'
        'Create a new database with the structure and contents of two temp directories:\n'
        '   treewalker --overwrite --output temp_files.sqlite --walk c:/temp d:/temp e:/temp\n'
        'Remove a subset of files already in a database:\n'
        '   treewalker --remove d:/temp/secret --output temp_files.sqlite\n'
        'Add previously generated files to the database:\n'
        '   treewalker --merge other_tmp_files.sqlite --output temp_files.sqlite\n'
        'Run treewalker with options from a .json configuration file:\n'
        '   treewalker -cfg options.json\n'
    )


def main():
    basicConfig(level=INFO)

    cfg = Config.startup(
        defaults={'merge': [], 'overwrite': False, 'remove': [], 'walk': [],
                  'rewrite': True, 'rewrite_admin': True},
        aliases={'o': 'output', 'w': 'walk', 'm': 'merge',
                 'ow': 'overwrite', 'rm': 'remove', 'h': 'help', '?': 'help',
                 'rw': 'rewrite', 'ra': 'rewrite_admin'},
        no_key_error=True
    )

    if cfg.get_as_type('help', bool, False):
        print_help()
        exit(0)

    overwrite = cfg.get_as_type('overwrite', bool, False)

    if cfg.merge:
        fns = cfg.merge
        if not isinstance(fns, list):
            fns = [fns]
        for fn in fns:
            if not Path(fn).is_file():
                error('File to merge not found: {}'.format(fn))
                exit(2)
        for fn in fns:
            info('Merging "{}" into "{}" (not processing further options)'.format(fn, cfg.output))
            with TreeWalker(cfg.output, overwrite=overwrite) as tree_walker:
                tree_walker.merge(fn)
        exit(0)

    if 'output' not in cfg:
        error('Provide "output" in configuration file, or on the command line as "--output <some filename>"')
        print_help()
        exit(1)

    if cfg['reindex']:
        print('Reindexing {}...'.format(cfg.output))
        with TreeWalker(cfg.output, overwrite=overwrite) as tree_walker:
            tree_walker.reindex()
        exit(0)

    if cfg['walk']:
        if not isinstance(cfg.walk, list):
            cfg.walk = [cfg.walk]
    else:
        cfg['walk'] = []
    if isinstance(cfg.output, list):
        cfg.walk.extend(cfg.output[1:])
        cfg.output = cfg.output[0]

    with TreeWalker(cfg.output, overwrite=overwrite,
                    rewrite=cfg.get_as_type('rewrite', bool, True),
                    rewrite_admin=cfg.get_as_type('rewrite_admin', bool, True)) as tree_walker:
        paths = cfg.walk + cfg.arguments[''][2:]

        for path in paths:
            tree_walker.update(path)

        if cfg.remove is not None:
            if not isinstance(cfg.remove, list):
                cfg.remove = [cfg.remove]
            for path in cfg.remove:
                if cfg.get_as_type('rewrite', bool, True):
                    path = tree_walker.rewrite_path(path)
                tree_walker.remove(path)


if __name__ == '__main__':
    main()
