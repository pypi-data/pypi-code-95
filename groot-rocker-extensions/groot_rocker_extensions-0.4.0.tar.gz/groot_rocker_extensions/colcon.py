#!/usr/bin/env python
#
# License: BSD
#   https://raw.githubusercontent.com/stonier/groot_rocker_extensions/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
Install colcon build tools.
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


class Colcon(groot_rocker.extensions.RockerExtension):
    """
    Installs tooling to support development with colcon.
    """
    @classmethod
    def get_name(cls) -> str:
        return re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()  # CamelCase to underscores

    @staticmethod
    def desired_extensions():
        return {"user"}

    def get_files(self, unused_cli_args):
        templates_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates")
        colcon_setup_path = os.path.join(templates_path, f"{Colcon.get_name()}_setup.bash")
        file = open(colcon_setup_path, "r")
        contents = file.read()
        file.close()
        return {"colcon_setup.bash": contents}

    def get_snippet(self, cli_args: typing.Dict[str, str]) -> str:
        snippet = pkgutil.get_data(
            "groot_rocker_extensions",
            f"templates/{Colcon.get_name()}.Dockerfile.em"
        ).decode('utf-8')

        substitutions = {}
        if 'user' in cli_args and cli_args['user']:
            substitutions['user_active'] = True
            substitutions["user_name"] = getattr(pwd.getpwuid(os.getuid()), 'pw_' + 'name')
        else:
            substitutions['user_active'] = False
        return em.expand(snippet, substitutions)

    @staticmethod
    def register_arguments(parser, defaults={}):
        parser.add_argument(
            '--colcon',
            action='store_true',
            default=defaults.get(Colcon.get_name(), None),
            help="install the colcon build tools"
        )
