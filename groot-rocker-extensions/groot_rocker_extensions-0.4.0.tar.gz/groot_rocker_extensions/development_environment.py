#!/usr/bin/env python
#
# License: BSD
#   https://raw.githubusercontent.com/stonier/groot_rocker_extensions/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
Configure and install tools for a generic linux development environment.
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


class DevelopmentEnvironment(groot_rocker.extensions.RockerExtension):
    """
    Installs various system dependencies and configures environment variables,
    locales, suitable for a generic linux development environment.
    """

    @classmethod
    def get_name(cls) -> str:
        return re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()  # CamelCase to underscores

    def get_snippet(self, cli_args: typing.Dict[str, str]) -> str:
        """
        """
        snippet = pkgutil.get_data(
            'groot_rocker_extensions',
            f"templates/{DevelopmentEnvironment.get_name()}.Dockerfile.em").decode('utf-8')
        substitutions = {
            "default_timezone": os.readlink("/etc/localtime"),
            "system_dependencies": (
               "apt-utils bash-completion build-essential curl debian-keyring "
               "debian-archive-keyring git iproute2 iputils-ping locales lsb-release "
               "net-tools openssh-client openssh-server python3-dev screen "
               "software-properties-common sudo vim wget xdot x11-apps "
            ),
            "language": "en_US.UTF-8",
            # Richest color set - https://www.gnu.org/software/gettext/manual/html_node/The-TERM-variable.html
            "terminal": "xterm-256color",
        }
        return em.expand(snippet, substitutions)

    def get_docker_args(self, unused_cli_args: typing.Dict[str, str]) -> str:
        return ''

    @staticmethod
    def register_arguments(parser, defaults={}):
        parser.add_argument(
            '--development-environment', '--devenv',
            action='store_true',
            default=defaults.get('development_environment', None),
            help="setup a generic development environment"
        )
