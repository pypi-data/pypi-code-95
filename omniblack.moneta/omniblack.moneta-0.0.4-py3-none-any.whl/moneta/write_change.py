from collections.abc import Iterable
from os import EX_OK, environ
from sys import exit
from contextlib import asynccontextmanager
from tempfile import NamedTemporaryFile
from functools import partial
from datetime import datetime
from io import StringIO
from calendar import month_abbr
from importlib.resources import read_text
from string import Template

from more_itertools import unique_everseen
from anyio import Path, run, wrap_file, open_process
from anyio.to_thread import run_sync
from git import Repo, DiffIndex
from git.util import Actor

from .version_package import VersionedPackage
from .change_parser import parse
from .yaml import yaml

from omniblack.repo import find_root, find_packages, init

release_branch = 'next'

change_levels = (
    'patch',
    'minor',
    'major',
)


class callable(type):
    async def __call__(cls, *args, **kwargs):
        self = super().__call__()
        return await self(*args, **kwargs)


class write_change(metaclass=callable):
    @staticmethod
    def find_parent_package(path: Path, packages: Iterable[VersionedPackage]):
        for pkg in packages:
            if pkg.path in path.parents:
                return pkg

    def get_files(self, diffs: DiffIndex):
        for diff in diffs:
            if diff.a_path is not None:
                yield self.root/diff.a_path

            if diff.b_path is not None and diff.b_path != diff.a_path:
                yield self.root/diff.b_path

    @asynccontextmanager
    async def temp_file(self, suffix=None):
        file = await run_sync(
            partial(
                NamedTemporaryFile,
                mode='w+',
                dir=self.root,
                suffix=suffix,
            ),
        )
        async_file = wrap_file(file)
        async with async_file:
            yield async_file

    async def edit_file(self, file):
        command = (
            environ.get('EDITOR', 'vim'),
            file.name,
        )

        process = await open_process(
            command,
            stdin=None,
            stdout=None,
            stderr=None,
        )

        await process.wait()

    def comment(self, text):
        if text:
            return f'% {text}\n'
        else:
            return '%\n'

    async def frontmatter(self, file, data: dict):
        await file.write('---\n')

        buffer = StringIO()
        yaml.dump(data=data, stream=buffer)

        await file.write(buffer.getvalue())
        await file.write('---\n')

    async def get_messages(self, changes):
        explainer_template = await run_sync(
            read_text,
            __package__,
            'message_explainer.txt',
        )

        template = Template(explainer_template)

        for change in changes:
            async with self.temp_file(suffix='.md') as msg_file:
                await msg_file.write('\n')
                explainer = template.substitute(
                    package=change.name,
                    branch=self.repo.active_branch,
                )

                await msg_file.writelines(
                    self.comment(line)
                    for line in explainer.splitlines()
                )
                await msg_file.seek(0)

                await self.edit_file(msg_file)

                msg = [
                    line
                    for line in await msg_file.readlines()
                    if not line.startswith('%')
                ]

                change.message = msg

    async def __call__(self, root: Path = None):
        await init()
        if root is None:
            self.root = await find_root()
        else:
            self.root = root

        self.repo = Repo(self.root)
        self.now = datetime.today()
        index = self.repo.index
        packages = set(await find_packages(self.root, VersionedPackage))

        diffs = index.diff('HEAD')
        changed_files = self.get_files(diffs)

        changed_packages = (
            self.find_parent_package(file, packages)
            for file in unique_everseen(changed_files)
        )

        name_and_full_path = (
            (pkg.config.name, pkg.path)
            for pkg in unique_everseen(changed_packages)
            if pkg is not None
        )

        name_and_path = (
            (name, path.relative_to(self.root))
            for name, path in name_and_full_path
        )

        level_select = tuple(
            (
                self.comment(path)
                + f'patch: {name}\n\n'
            )
            for name, path in name_and_path
        )

        if not level_select:
            print('No changes staged.')
            exit(0)

        async with self.temp_file() as async_file:
            await async_file.writelines(level_select)
            explainer = await run_sync(
                read_text,
                __package__,
                'severity_explainer.txt',
            )
            explainer_lines = explainer.splitlines()
            await async_file.writelines(
                self.comment(line)
                for line in explainer_lines
            )
            await async_file.seek(0)

            await self.edit_file(async_file)

            changes = await parse(async_file)

        missing_messages = (
            change
            for change in changes
            if not change.message
        )

        await self.get_messages(missing_messages)

        changes_dir = self.root/'.changes'/str(self.now.year)

        await changes_dir.mkdir(parents=True, exist_ok=True)

        author = Actor.author(self.repo.config_reader())
        paths = []
        for change in changes:
            month_str = month_abbr[self.now.month].lower()
            time_str = f'{self.now.hour}:{self.now.minute}'
            date_str = f'{month_str}-{self.now.day}T{time_str}'
            name = f'{change.name}-{date_str}.md'
            path = changes_dir/name.replace('/', '-')
            paths.append(path)

            async with await path.open('x') as file:
                await self.frontmatter(file=file, data=dict(
                    author=author.name,
                    email=author.email,
                    date=self.now,
                    severity=change.severity,
                    package=change.name
                ))

                await file.writelines(change.message)

        index.add(
            tuple(
                path.__fspath__()
                for path in paths
            ),
            write=True,
        )


def main():
    exit(run(write_change) or EX_OK)


if __name__ == '__main__':
    main()
