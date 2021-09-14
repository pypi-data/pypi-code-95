#!/usr/bin/env python
#
# License: BSD
#   https://raw.githubusercontent.com/stonier/groot_rocker_extensions/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
Transfer a user's git configuration to the docker container. This extension
really only makes sense with the 'user' extension, but won't fail if that
has not been activated.
"""

##############################################################################
# Imports
##############################################################################

import os
import re
import typing

import groot_rocker

##############################################################################
# Extension
##############################################################################


class Git(groot_rocker.extensions.RockerExtension):
    """
    Transfers system and user (if the user extension has been selected) git
    configuration files to the docker container as volumes.
    """
    @classmethod
    def get_name(cls) -> str:
        return re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()  # CamelCase to underscores

    def precondition_environment(self, unused_cli_args: typing.Dict[str, str]):
        pass

    def validate_environment(self, unused_cli_args: typing.Dict[str, str]):
        pass

    def get_preamble(self, unused_cli_args: typing.Dict[str, str]) -> str:
        return ''

    def get_snippet(self, unused_cli_args: typing.Dict[str, str]) -> str:
        return ''

    def get_docker_args(self, cli_args: typing.Dict[str, str]) -> str:
        args = ''
        system_gitconfig = '/etc/gitconfig'
        user_gitconfig = os.path.expanduser('~/.gitconfig')
        user_gitconfig_target = '/root/.gitconfig'
        if 'user' in cli_args and cli_args['user']:
            user_gitconfig_target = user_gitconfig
        if os.path.exists(system_gitconfig):
            args += ' -v {system_gitconfig}:{system_gitconfig}:ro'.format(**locals())
        if os.path.exists(user_gitconfig):
            args += ' -v {user_gitconfig}:{user_gitconfig_target}:ro'.format(**locals())
        return args

    @staticmethod
    def register_arguments(parser, defaults={}):
        parser.add_argument(
            '--git',
            action='store_true',
            default=defaults.get('git', None),
            help="use host settings (/etc/gitconfig and ~/.gitconfig)"
        )
