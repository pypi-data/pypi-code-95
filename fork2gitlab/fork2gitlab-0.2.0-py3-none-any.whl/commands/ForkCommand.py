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
import logging

import gitlab
from cliff.command import Command
from gitlab.v4.objects import VISIBILITY_PUBLIC, VISIBILITY_PRIVATE, VISIBILITY_INTERNAL

from fork2gitlab.utils import DOT_GIT, remove_ext


class ForkCommand(Command):
    """
    Creates a fork of a project on gitlab and sets it up to mirror
     the given repository automatically.
    """

    def get_parser(self, prog_name):
        parser = super(ForkCommand, self).get_parser(prog_name)
        parser.add_argument("-n", "--name", help="Name of the repo on gitlab")
        parser.add_argument(
            "--visibility",
            default=VISIBILITY_PUBLIC,
            choices=(
                VISIBILITY_PRIVATE,
                VISIBILITY_INTERNAL,
                VISIBILITY_PUBLIC
            ))
        parser.add_argument("url", help="URL to fork from. Should be accessible to gitlab")

        return parser

    def take_action(self, parsed_args):
        gl = gitlab.Gitlab.from_config()
        gl.auth()

        result = gl.projects.create(
            name=self._get_name(parsed_args),
            import_url=parsed_args.url,
            mirror=True,
            visibility=parsed_args.visibility,
        )

        logging.info("Created new repo at %s", result.web_url)

    def _get_name(self, parsed_args):
        name = parsed_args.name

        if not name:
            tail: str = parsed_args.url.split("/")[-1]
            name = remove_ext(tail, DOT_GIT)
        return name
