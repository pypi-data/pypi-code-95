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
import shlex

from . import utilities

##############################################################################
# Tests
##############################################################################


class Ssh(utilities.ExtensionTestCase):

    # disabled until persistent + SSH_AUTH_SOCK solution sis found
    def do_not_ssh_auth_sock(self):
        mock_cli_args = {}

        # with SSH_AUTH_SOCK set
        os.environ['SSH_AUTH_SOCK'] = 'foo'
        args = self.extension.get_docker_args(mock_cli_args)
        string_to_check = '-e SSH_AUTH_SOCK --volume ' + shlex.quote('{SSH_AUTH_SOCK}:{SSH_AUTH_SOCK}'.format(**os.environ))
        utilities.assert_details(
            text="ssh_auth_sock: detect and set run args",
            expected=True,
            result=string_to_check in args
        )
        self.assertIn(string_to_check, args)

        # without SSH_AUTH_SOCK set
        del os.environ['SSH_AUTH_SOCK']
        args = self.extension.get_docker_args(mock_cli_args)
        utilities.assert_details(
            text="ssh_auth_sock: detect not present",
            expected=False,
            result="SSH_AUTH_SOCK" in args
        )
        self.assertNotIn('SSH_AUTH_SOCK', args)
