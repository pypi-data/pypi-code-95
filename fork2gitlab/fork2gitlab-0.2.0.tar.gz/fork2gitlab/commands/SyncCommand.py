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
import argparse
import logging
from enum import Enum
from pathlib import Path
from subprocess import CalledProcessError
from tempfile import TemporaryDirectory

import gitlab
from cliff.command import Command

from fork2gitlab import git
from fork2gitlab.utils import get_authorized_url, str2int


class SyncCommand(Command):
    """
    Synchronize with the upstream repository.

    If there are no merge conflicts, the upstream changes are integrated into the fork and pushed.
    Merge conflicts require human resolution and thus a merge request is created on gitlab.

    Return codes:

        * 0 - OK
        * 1 - An error occurred
        * 2 - Merge request created
    """

    class ReturnCode(Enum):
        OK = 0
        ERROR = 1
        MERGE_REQUEST = 2

    def take_action(self, parsed_args):
        group_path, _, project_name = parsed_args.project_name.rpartition("/")
        target_branch = parsed_args.target_branch
        source_branch = parsed_args.source_branch
        logging.info("group_path: %s, project_name: %s, branch: %s",
                     group_path, project_name, target_branch)

        gl = gitlab.Gitlab.from_config()
        gl.auth()

        # Find the group project
        if group_path:
            group = next(iter(
                group
                for group in gl.groups.list(search=group_path)
                if group.full_path == group_path
            ), None)
            if not group:
                logging.error("Unknown group path %s", group_path)
                return
            projects = [
                project
                for project in group.projects.list(search=project_name)
                if project.path == project_name
            ]
        else:
            user = gl.users.get(gl.user.id)
            projects = user.projects.list(search=project_name)

        len_projects = len(projects)
        if len_projects == 0:
            logging.error("Unknown project for %s", group if group else user.username)
            return

        interactive = not parsed_args.non_interactive
        index = 0

        # Interactively select the project
        if interactive and len_projects > 1:
            while True:
                logging.info("Select a project")
                for i, project in enumerate(projects):
                    logging.info("\t%s: %s at %s", i, project.name, project.web_url)
                selection = str2int(input("Selection: "))
                if selection is not None and (0 <= selection < len_projects):
                    index = selection
                    break

        # Attempt the merge
        project = projects[index]
        with TemporaryDirectory(prefix="fork2gitlab") as temp_d:
            repo_path = Path(temp_d) / project_name
            git_http = project.http_url_to_repo
            logging.info("Cloning %s to '%s'", git_http, repo_path)
            git.clone(git_http, repo_path)

            # Checkout target_branch
            git.checkout(repo_path, target_branch)

            # Attempt to merge source into target
            try:
                git.merge(repo_path, git_http, source_branch)
                logging.info("Successfully merged %s into %s", source_branch, target_branch)
                logging.debug("Setting remote with private token")
                git.set_remote(
                    repo_path,
                    get_authorized_url(git_http, gl.user.name, gl.private_token)
                )
                logging.info("Pushing merged branch %s", target_branch)
                git.push(repo_path)
            except CalledProcessError as process_error:
                # Can't merge
                logging.warning(
                    "Couldn't merge %s into %s: %s",
                    source_branch, target_branch,
                    process_error
                )
                logging.info("Create pull request to manual action")
                project.mergerequests.create(data=dict(
                    title=f"Merge {source_branch} into {target_branch}",
                    description="Automatically created due to merge conflict",
                    id=project.get_id(),
                    source_branch=source_branch,
                    target_branch=target_branch
                ))
                return self.ReturnCode.MERGE_REQUEST

    def get_parser(self, prog_name):
        parser = super(SyncCommand, self).get_parser(prog_name)

        parser.add_argument(
            "-n", "--non-interactive",
            help="Don't ask any questions",
            action="store_true",
        )

        parser.add_argument(
            "-s", "--source-branch",
            default="master",
            help="Which branch to merge changes from",
        )

        parser.add_argument(
            "project_name",
            help="Project on gitlab. "
                 "If it doesn't contain slashes (/) then it has to be your personal project."
                 "Slashes indicate it's in a group with the first components being the group path"
                 " and the last one the project name"
                 "Since you're using your account it has to be accessible by you."
        )
        parser.add_argument(
            "target_branch",
            help="Where the upstream changes should be merged into"
        )

        return parser

    @staticmethod
    def _check_path(path_str: str) -> None:
        path = Path(path_str)
        if not path.exists():
            raise argparse.ArgumentTypeError(f"Path '{path_str}' must exist")
        return path
