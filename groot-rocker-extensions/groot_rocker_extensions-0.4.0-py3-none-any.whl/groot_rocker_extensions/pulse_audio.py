#!/usr/bin/env python
#
# License: BSD
#   https://raw.githubusercontent.com/stonier/groot_rocker_extensions/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
Forward PulseAudio configuration into the container. Only tested in Ubuntu 18.
"""

##############################################################################
# Imports
##############################################################################

import em
import grp
import os
import pathlib
import pkgutil
import pwd
import re
import typing

import groot_rocker

##############################################################################
# Extension
##############################################################################


class PulseAudio(groot_rocker.extensions.RockerExtension):
    """
    Forward PulseAudio configuration into the container.
    This will not work without --user.

    This extension requires a logged in desktop user with
    the defualt pulse audio configuration. One problem with this is that
    the exact same user permissions are required within and without, which
    makes it unsuitable for headless systems.

    This can be worked around, but it likely requires some level of
    host configuration. Refer to

      https://github.com/stonier/groot_rocker_extensions/issues/31

    Regardless, this least-effort implementation is still desirable
    and useful for logged in desktop users.

    Test with the 'speaker-test' utility that gets installed with this
    extension.

    .. code=block:: bash

       speaker-test --channels=2 --nloops=1 --test=wav --device=default

    """
    @classmethod
    def get_name(cls) -> str:
        return re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()  # CamelCase to underscores

    def precondition_environment(self, unused_cli_args: typing.Dict[str, str]):
        pass

    def validate_environment(self, unused_cli_args: typing.Dict[str, str]):
        pulse_dir = f"/run/user/{os.getuid()}/pulse"
        if not os.path.exists(pulse_dir):
            raise groot_rocker.core.ValidateError(
                f"user's pulseaudio not found [{pulse_dir}]"
            )

    @staticmethod
    def required_extensions():
        return {"user"}

    def get_preamble(self, unused_cli_args: typing.Dict[str, str]) -> str:
        return ''

    def get_snippet(self, cli_args: typing.Dict[str, str]) -> str:
        container_pulse_socket = os.path.join(os.getenv('XDG_RUNTIME_DIR'), "pulse", "native")
        snippet = pkgutil.get_data(
            'groot_rocker_extensions',
            f"templates/{PulseAudio.get_name()}_snippet.Dockerfile.em").decode('utf-8')
        substitutions = {
            "audio_dependencies": (
                "alsa-utils libasound2-plugins"
            ),
            "pulse_socket": container_pulse_socket,
            # 'user' is a required extension
            "user_active": True,
            "user_id": os.getuid(),
            "user_name": getattr(pwd.getpwuid(os.getuid()), 'pw_' + 'name')
        }
        return em.expand(snippet, substitutions)

    def get_docker_args(self, cli_args: typing.Dict[str, str]) -> str:
        # XDG_RUNTIME_DIR
        #   defn: location for a user's runtime artifacts as spec'd by freedesktop
        #   note: this requires a host system with a logged in user as it is only
        #         configured upon login
        host_user_runtime_dir = pathlib.Path(os.getenv('XDG_RUNTIME_DIR'))
        substitutions = {
            "audio_group_id": f"{grp.getgrnam('audio').gr_gid}",
            "host_user_pulse_dir": os.path.join(host_user_runtime_dir, "pulse")
        }
        args = (
            " --device /dev/snd "
            " -v /usr/share/alsa:/usr/share/alsa "
            " -v %(host_user_pulse_dir)s:%(host_user_pulse_dir)s "
            " -e PULSE_SERVER=unix:%(host_user_pulse_dir)s/native "
            " --group-add %(audio_group_id)s "
        )
        return args % substitutions

    @staticmethod
    def register_arguments(parser, defaults={}):
        parser.add_argument(
            '--pulse-audio',
            action='store_true',
            default=defaults.get(PulseAudio.get_name(), None),
            help="ride along on the host user's pulseaudio"
        )
