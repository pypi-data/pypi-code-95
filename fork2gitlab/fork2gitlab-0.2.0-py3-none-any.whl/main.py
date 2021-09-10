"""
fork2gitlab
Copyright (C) 2020 LoveIsGrief

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import sys

from cliff.app import App
from cliff.commandmanager import CommandManager

from fork2gitlab import __version__
from fork2gitlab.commands.ForkCommand import ForkCommand
from fork2gitlab.commands.SyncCommand import SyncCommand


class F2GCommandManager(CommandManager):
    def __init__(self):
        super().__init__("fork2gitlab")

    def load_commands(self, namespace):
        self.add_command("fork", ForkCommand)
        self.add_command("sync", SyncCommand)


class Fork2Gitlab(App):
    """
    A script to help forking a branch from a git repo to gitlab
     and periodically integrating changes from upstream into the new branch.
    """

    def __init__(self):
        super(Fork2Gitlab, self).__init__(
            description=self.__doc__,
            version=__version__,
            command_manager=F2GCommandManager()
        )


def main(argv=sys.argv[1:]):
    f2g = Fork2Gitlab()
    return f2g.run(argv or ["help"])


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
