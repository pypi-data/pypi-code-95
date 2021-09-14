#!/usr/bin/env python
#
# License: BSD
#   https://raw.githubusercontent.com/stonier/groot_rocker_extensions/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################
"""
Export a coloured, named prompt to ~/.bash_profile on container creation.
"""

##############################################################################
# Imports
##############################################################################

import em
import pkgutil
import os
import pwd
import re
import typing

import groot_rocker

##############################################################################
# Extension
##############################################################################


class NamedPrompt(groot_rocker.extensions.RockerExtension):

    @classmethod
    def get_name(cls) -> str:
        return re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()  # CamelCase to underscores

    def precondition_environment(self, unused_cli_args: typing.Dict[str, str]):
        pass

    def validate_environment(self, unused_cli_args: typing.Dict[str, str]):
        pass

    @staticmethod
    def desired_extensions():
        return {"user"}

    def get_preamble(self, unused_cli_args: typing.Dict[str, str]) -> str:
        return ''

    def get_snippet(self, cli_args: typing.Dict[str, str]) -> str:
        snippet = pkgutil.get_data(
            'groot_rocker_extensions',
            'templates/named_prompt.Dockerfile.em'
        ).decode('utf-8')
        substitutions = {}
        if 'user' in cli_args and cli_args['user']:
            userinfo = pwd.getpwuid(os.getuid())
            substitutions['user_name'] = getattr(userinfo, 'pw_' + 'name')
            substitutions['home_dir'] = f"/home/{substitutions['user_name']}"
        else:
            substitutions['user_name'] = "root"
            substitutions['home_dir'] = "/root"
        if 'container_name' in cli_args and cli_args['container_name']:
            substitutions['container_name'] = cli_args['container_name']
        else:
            substitutions['container_name'] = r'\h'
        return em.expand(snippet, substitutions)

    def get_docker_args(self, unused_cli_args: typing.Dict[str, str]) -> str:
        return ""

    @staticmethod
    def register_arguments(parser, defaults={}):
        # TODO: what to do with the defaults arg?
        parser.add_argument(
            '--named-prompt',
            action='store_true',
            help='export a named prompt via PS1 to ~/.bash_profile'
        )
