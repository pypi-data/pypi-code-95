from functools import wraps, partial
from itertools import islice, takewhile, chain
from logging import getLogger
from os import environ
from pathlib import Path as SyncPath
from subprocess import CalledProcessError
from typing import Mapping

from anyio import create_task_group, run_process, Path
from anyio.to_thread import run_sync
from box import Box
from dataclasses import dataclass
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern
from public import public

from .model import model
from .package_group import PackageGroup

log = getLogger(__name__)


def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))


class AsyncIterator:
    def __init__(self, iterator, batch_size=10):
        self.iter = iter(iterator)
        self.batch_size = batch_size
        self.batch = []
        self.done = False

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self.batch and not self.done:
            await run_sync(
                self.__next,
                cancellable=True,
            )

        if not self.batch and self.done:
            raise StopAsyncIteration()

        return self.batch.pop()

    def __next(self):
        self.batch = take(self.batch_size, self.iter)
        self.batch.reverse()
        if len(self.batch) != self.batch_size:
            self.done = True


async def iterdir(path):
    sync_path = SyncPath(path)

    async for path in AsyncIterator(sync_path.iterdir()):
        yield Path(path)


def async_cache(func):
    cache = {}

    @wraps(func)
    async def cache_func(*args):
        if args in cache:
            return cache[args]

        ret_val = await func(*args)
        cache[args] = ret_val
        return ret_val

    return cache_func


def async_path_cache(func):
    cache = {}

    @wraps(func)
    async def cache_func(search_path: Path):
        if search_path in cache:
            return cache[search_path]

        ret_val = await func(search_path)
        cache[search_path] = ret_val
        searched_paths = takewhile(
            lambda path: path != ret_val.parent,
            search_path.parents,
        )
        for path in searched_paths:
            cache[path] = ret_val

        return ret_val

    return cache_func


@public
async def find_root(search_path: Path = None):
    if 'SRC' in environ:
        return Path(environ['SRC'])
    elif 'GIT_WORK_TREE' in environ:
        return Path(environ['GIT_WORK_TREE'])
    else:
        if search_path is None:
            search_path = await Path.cwd()
        else:
            search_path = search_path.resolve(strict=True)

        try:
            result = await run_process(
                ['git', 'rev-parse', '--show-toplevel'],
                cwd=search_path,
            )
            path_str = result.stdout.decode().strip()
            return Path(path_str)
        except CalledProcessError:
            return None


# In priority order
js_manifest_suffixes = ('json', 'yaml', 'yml', 'json5')

possible_js_manifests = tuple(
    f'package.{suffix}'
    for suffix in js_manifest_suffixes
)

js_manifests_set = set(possible_js_manifests)

possible_py_manifests = ('pyproject.toml', )
py_manifests_set = set(possible_py_manifests)

# In priority order
package_suffixes = ('yaml', 'yml', 'toml', 'json5', 'json')

possible_packages_configs = tuple(
    f'package_config.{suffix}'
    for suffix in package_suffixes
)

package_set = set(possible_packages_configs)


def get_priority_file(found_paths, files):
    if not found_paths:
        return None

    sorted_files = sorted(
        found_paths,
        key=lambda file: files.index(file.name),
    )

    return sorted_files[0]


@public
@dataclass
class Package:
    path: Path
    src_dir: Path
    config: Mapping
    config_path: Path
    javascript: Mapping
    js_path: Path
    python: Mapping
    py_path: Path

    def __hash__(self):
        return hash(str(self.path))

    def __eq__(self, other):
        if isinstance(other, Package):
            return str(self.path) == str(other.path)
        else:
            return NotImplemented

    async def resolvePath(self, path):
        return self.path.joinpath(path)

    @classmethod
    async def create(cls, config_path, path, js_path, py_path):
        src_dir = path/'src'
        files = {}
        async with create_task_group() as tg:
            tg.start_soon(
                cls.__load_config,
                config_path,
                files,
            )
            tg.start_soon(
                cls.__load_js,
                js_path,
                files,
            )
            tg.start_soon(
                cls.__load_py,
                py_path,
                files,
            )

        config = files['config']
        javascript = files['js']
        python = files['py']

        return cls(
            path=path,
            src_dir=src_dir,
            config=config,
            config_path=config_path,
            javascript=javascript,
            js_path=js_path,
            python=python,
            py_path=py_path,
        )

    @classmethod
    @model.require
    async def __load_config(self, path, files):
        result = await (model
                        .structs.package_config.load_file(SyncPath(path)))
        files['config'] = result

    @classmethod
    async def __load_js(self, path, files):
        if path is None:
            files['js'] = None
            return

        result = await run_sync(partial(Box.from_json, filename=path))
        files['js'] = result

    @classmethod
    async def __load_py(self, path, files):
        if path is None:
            files['py'] = None
            return

        result = await run_sync(partial(Box.from_toml, filename=path))
        files['py'] = result


@public
async def find_packages(search_root: Path = None, Package: Package = Package):
    root = await find_root(search_root)
    ignore_path = root/'.gitignore'

    try:
        async with await ignore_path.open() as file:
            lines = await file.readlines()
            stripped_lines = (
                line.strip()
                for line in lines
            )

            lines = tuple(
                line
                for line in stripped_lines
                if line
                if not line.startswith('#')
            )
            log.info(lines)

            ignores = PathSpec.from_lines(
                GitWildMatchPattern,
                chain(lines, ('.git', )),
            )
    except FileNotFoundError:
        ignores = PathSpec([])

    found_packages = PackageGroup()
    await _find_packages(
        root,
        ignores,
        found_packages,
        Package,
    )

    log.info('Found all packages')

    return found_packages


async def _find_packages(
    search_dir: Path,
    ignores,
    found_packages,
    Package,
):
    found_js_manifests = []
    found_package_configs = []
    found_py_manifests = []
    sub_dirs = []
    async for entry in iterdir(search_dir):
        is_file = await entry.is_file()
        is_dir = await entry.is_dir()

        entry_str = str(entry)

        if is_dir:
            entry_str += '/'

        if ignores.match_file(entry_str):
            continue

        if is_file:
            if entry.name in js_manifests_set:
                found_js_manifests.append(entry)
            elif entry.name in py_manifests_set:
                found_py_manifests.append(entry)
            elif entry.name in package_set:
                found_package_configs.append(entry)
        elif is_dir:
            sub_dirs.append(entry)

    found_lang_manifest = found_js_manifests or found_py_manifests
    if found_package_configs and found_lang_manifest:
        pkg_path = get_priority_file(
            found_package_configs,
            possible_packages_configs,
        )

        js_man_path = get_priority_file(
            found_js_manifests,
            possible_js_manifests,
        )

        py_man_path = get_priority_file(
            found_py_manifests,
            possible_py_manifests,
        )

        package = await Package.create(
            config_path=pkg_path,
            js_path=js_man_path,
            py_path=py_man_path,
            path=search_dir,
        )

        found_packages.append(package)
    else:
        async with create_task_group() as tg:
            for dir in sub_dirs:
                tg.start_soon(
                    _find_packages,
                    dir,
                    ignores,
                    found_packages,
                    Package,
                )
