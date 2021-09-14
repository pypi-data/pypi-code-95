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
import pwd
import re
import typing

import groot_rocker

##############################################################################
# Extension
##############################################################################


class User(groot_rocker.extensions.RockerExtension):
    """
    Map the currently executing user to the docker environment. This essentially
    just recreates user and group information in the image. It also specifies
    the WORKDIR as the home directory if not otherwise set by the WorkDirectory
    extension.
    """

    @classmethod
    def get_name(cls) -> str:
        return re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()  # CamelCase to underscores

    def get_environment_subs(self) -> typing.Dict[str, str]:
        user_vars = ['name', 'uid', 'gid', 'gecos', 'dir', 'shell']
        userinfo = pwd.getpwuid(os.getuid())
        return {
            k: getattr(userinfo, 'pw_' + k)
            for k in user_vars
        }

    def precondition_environment(self, unused_cli_args: typing.Dict[str, str]):
        pass

    def validate_environment(self, unused_cli_args: typing.Dict[str, str]):
        pass

    def get_preamble(self, unused_cli_args: typing.Dict[str, str]) -> str:
        return ''

    def get_snippet(self, cli_args: typing.Dict[str, str]) -> str:
        """
        """
        snippet = pkgutil.get_data('groot_rocker_extensions', f"templates/{User.get_name()}.Dockerfile.em").decode('utf-8')
        substitutions = self.get_environment_subs()
        substitutions['home_extension_active'] = True if 'home' in cli_args and cli_args['home'] else False
        substitutions['work_directory_active'] = True if 'work_directory' in cli_args and cli_args['work_directory'] else False
        return em.expand(snippet, substitutions)

    def get_docker_args(self, unused_cli_args: typing.Dict[str, str]) -> str:
        return ''

    @staticmethod
    def register_arguments(parser, defaults={}):
        parser.add_argument(
            '--user',
            action='store_true',
            default=defaults.get('user', None),
            help="mount the current user's id and run as that user"
        )
