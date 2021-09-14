#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# License: BSD
#   https://raw.githubusercontent.com/stonier/groot_rocker_extensions/devel/LICENSE
#

##############################################################################
# Imports
##############################################################################

import os

from . import utilities

##############################################################################
# Tests
##############################################################################


class PulseAudio(utilities.ExtensionTestCase):

    def test_pulse_server_env_variable(self):
        mock_cli_args = {}

        os.environ['XDG_RUNTIME_DIR'] = '/run/user/1000'

        args = self.extension.get_docker_args(mock_cli_args)
        string_to_check = '-e PULSE_SERVER=unix:'
        utilities.assert_details(
            text="Set PULSE_SERVER Env Variable",
            expected=True,
            result=string_to_check in args
        )
        self.assertIn(string_to_check, args)
