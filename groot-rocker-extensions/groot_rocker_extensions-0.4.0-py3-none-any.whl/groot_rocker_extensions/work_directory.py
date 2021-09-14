#!/usr/bin/env python
#
# License: BSD
#   https://raw.githubusercontent.com/stonier/groot_rocker_extensions/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
Switch to the specified working directory on entry into the container.
"""

##############################################################################
# Imports
##############################################################################

import em
import os
import pkgutil
import re
import typing

import groot_rocker

##############################################################################
# Extension
##############################################################################


class WorkDirectory(groot_rocker.extensions.RockerExtension):
    """
    Be robust to '~', but otherwise just directly pass in the
    specified working directory to the dockerfile WORKDIR variable.

    .. todo:: check that the working directory actually exists in the image
    """

    @classmethod
    def get_name(cls) -> str:
        return re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()  # CamelCase to underscores

    def precondition_environment(self, unused_cli_args: typing.Dict[str, str]):
        pass

    def validate_environment(self, unused_cli_args: typing.Dict[str, str]):
        pass

    def get_preamble(self, unused_cli_args: typing.Dict[str, str]):
        return ''

    def get_snippet(self, cli_args: typing.Dict[str, str]):
        work_directory = cli_args[WorkDirectory.get_name()]
        if work_directory == "~":  # expand
            work_directory = os.path.expanduser("~")
        snippet = pkgutil.get_data(
            "groot_rocker_extensions",
            f"templates/{WorkDirectory.get_name()}.Dockerfile.em"
        ).decode('utf-8')
        substitutions = {WorkDirectory.get_name(): work_directory}
        return em.expand(snippet, substitutions)

    def get_docker_args(self, unused_cli_args: typing.Dict[str, str]):
        return ''

    @staticmethod
    def register_arguments(parser, defaults={}):
        parser.add_argument(
            '--work-directory',
            type=str,
            default=defaults.get(WorkDirectory.get_name(), None),
            help='set the default work directory on container entry'
        )
