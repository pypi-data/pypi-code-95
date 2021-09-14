#!/usr/bin/env python
#
# License: BSD
#   https://raw.githubusercontent.com/stonier/groot_rocker_extensions/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
Enable nvidia in the docker image/container.
"""

##############################################################################
# Imports
##############################################################################

import em
import pkgutil
import re
import sys
import typing

import groot_rocker
import groot_rocker.console as console

##############################################################################
# Extension
##############################################################################


class Nvidia(groot_rocker.extensions.RockerExtension):
    """
    This class pulls the nvidia docker images and incorporates it on top
    of an existing base image.
    """
    @classmethod
    def get_name(cls) -> str:
        return re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()  # CamelCase to underscores

    def __init__(self):
        self.supported_distros = ['Ubuntu']  # 'Debian GNU/Linux'
        self.supported_versions = ['18.04', '20.04']  # '10'

    def get_environment_subs(self, cli_args: typing.Dict[str, str] = {}) -> typing.Dict[str, str]:
        substitutions = {}

        # non static elements test every time
        detected_os = groot_rocker.os_detector.detect_os(
            cli_args['base_image'],
            print,
            nocache=cli_args.get('nocache', False)
        )
        if detected_os is None:
            console.error(f"unable to detect os for base image '{cli_args['base_image']}', maybe the base image does not exist")
            sys.exit(1)
        dist, ver, unused_codename = detected_os

        substitutions['image_distro_id'] = dist
        if substitutions['image_distro_id'] not in self.supported_distros:
            console.error(f"distro id '{substitutions['image_distro_id']}' not in supported list {self.supported_distros}")
            sys.exit(1)
        else:
            # for embedding in the nvidia_preamble snippet to identify the nvidia opengl image
            substitutions['image_distro_id'] = substitutions['image_distro_id'].lower()
        substitutions['image_distro_version'] = ver
        if substitutions['image_distro_version'] not in self.supported_versions:
            console.error(f"distro '{dist}', version '{ver}' not in supported list {self.supported_versions}")
            sys.exit(1)
            # TODO(tfoote) add a standard mechanism for checking preconditions and disabling plugins
        return substitutions

    def precondition_environment(self, unused_cli_args: typing.Dict[str, str]):
        pass

    def validate_environment(self, unused_cli_args: typing.Dict[str, str]):
        pass

    def get_preamble(self, cli_args: typing.Dict[str, str]) -> str:
        preamble = pkgutil.get_data('groot_rocker_extensions', f"templates/{Nvidia.get_name()}_preamble.Dockerfile.em").decode('utf-8')
        substitutions = self.get_environment_subs(cli_args)
        return em.expand(preamble, substitutions)

    def get_snippet(self, cli_args: typing.Dict[str, str]) -> str:
        snippet = pkgutil.get_data('groot_rocker_extensions', f"templates/{Nvidia.get_name()}_snippet.Dockerfile.em").decode('utf-8')
        substitutions = self.get_environment_subs(cli_args)
        return em.expand(snippet, substitutions)

    def get_docker_args(self, unused_cli_args: typing.Dict[str, str]) -> str:
        return ''' --gpus 'all,"capabilities=graphics,utility,display,video,compute"' --volume /tmp/.X11-unix:/tmp/.X11-unix:ro --env=DISPLAY'''

    @staticmethod
    def register_arguments(parser, defaults={}):
        parser.add_argument(
            '--nvidia',
            action='store_true',
            default=defaults.get('nvidia', None),
            help="enable nvidia"
        )
