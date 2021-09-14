#!/usr/bin/env python
#
# License: BSD
#   https://raw.githubusercontent.com/stonier/groot_rocker_extensions/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
Mount host paths in the docker container via docker's bind mechanism.
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


class Bind(groot_rocker.extensions.RockerExtension):
    """
    Mounts host paths to target paths in the container via the docker bind
    mechanism.

    .. note:

       Volumes are preferred in a docker-verse, but these cannot operate on
       existing host paths. Bind however, comes with the entanglement of
       permissions.

    .. tip:

       In most cases, you would use this extension with the
      'user' extension to ensure internal and external permissions align.
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
        args = []
        for mount in cli_args['bind']:
            for d in mount.split(" "):
                if ":" in d:
                    src, dst = d.split(":")
                else:
                    src = d
                    dst = d
                src = os.path.abspath(src)
                args.append(f"--mount type=bind,source={src},target={dst}")
        return ' ' + ' '.join(args)

    @staticmethod
    def register_arguments(parser, defaults={}):
        # Be a little robust to user input defaults. Very often there is just
        # one argument, this allows people to pass it in as a string, not a list
        default = defaults.get(Bind.get_name(), [])
        if isinstance(default, str):
            default = [default]
        parser.add_argument(
            '--bind',
            type=str,
            nargs='+',
            metavar="SOURCE:TARGET",
            default=default,
            help="bind host folders at arbitrary mount points"
        )
