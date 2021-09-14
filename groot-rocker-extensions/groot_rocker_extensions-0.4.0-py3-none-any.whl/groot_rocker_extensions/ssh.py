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
import shlex
import typing

import groot_rocker

##############################################################################
# Extension
##############################################################################


class Ssh(groot_rocker.extensions.RockerExtension):
    """
    Does a few ssh related activities:

     * Image: ensures ssh server and client debians are installed.
     * Container: forwards the SSH_AUTH_SOCK agent properties into the container
     * Container: if the user extension has been applied and ~/.ssh exists, mount it
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

    def get_snippet(self, unused_cli_args: typing.Dict[str, str]):
        snippet = pkgutil.get_data(
            "groot_rocker_extensions",
            f"templates/{Ssh.get_name()}.Dockerfile.em"
        ).decode('utf-8')
        return em.expand(snippet, {})

    def get_docker_args(self, cli_args: typing.Dict[str, str]):
        """
        It would be useful to enable SSH_AUTH_SOCK for passwordless logins.
        This, however, fails with persistent containers since this hardcodes SSH_AUTH_SOCK
        at the time of calling docker run to create the container. If the host reboots,
        the location is no longer valid and a call to 'container start <name> -i' will
        fail as reported in #27.
        """
        args = ''
        # if 'SSH_AUTH_SOCK' in os.environ:
        #     args += " -e SSH_AUTH_SOCK"
        #     args += " --volume " + shlex.quote("{SSH_AUTH_SOCK}:{SSH_AUTH_SOCK}".format(**os.environ))
        return args

    @staticmethod
    def register_arguments(parser, defaults={}):
        parser.add_argument(
            '--ssh',
            action="store_true",
            default=defaults.get(Ssh.get_name(), None),
            help='configures the container with ssh capabilities'
        )
