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


class Git(utilities.ExtensionTestCase):

    def test_detection(self):
        """
        This is not an ideal test - it depends on whether or not the
        system that runs the test has git configuration or not.
        Ideally, that ought to be mocked in some way. At the least though
        it provides a useful development test with the developer's
        system.
        """
        mock_cli_args = {}
        self.assertEqual(self.extension.get_snippet(mock_cli_args), '')
        self.assertEqual(self.extension.get_preamble(mock_cli_args), '')
        args = self.extension.get_docker_args(mock_cli_args)

        system_gitconfig = '/etc/gitconfig'
        user_gitconfig = os.path.expanduser('~/.gitconfig')
        user_gitconfig_target = '/root/.gitconfig'
        utilities.assert_details(
            text=f"Mount {system_gitconfig}",
            expected=os.path.exists(system_gitconfig),
            result=(f"-v {system_gitconfig}:{system_gitconfig}" in args)
        )
        if os.path.exists(system_gitconfig):
            self.assertIn('-v %s:%s' % (system_gitconfig, system_gitconfig), args)
        utilities.assert_details(
            text=f"Mount {user_gitconfig_target}",
            expected=os.path.exists(user_gitconfig),
            result=(f"-v {user_gitconfig}:{user_gitconfig_target}" in args)
        )
        if os.path.exists(user_gitconfig):
            self.assertIn('-v %s:%s' % (user_gitconfig, user_gitconfig_target), args)

        # Test with user "enabled"
        mock_cli_args = {'user': True}
        user_args = self.extension.get_docker_args(mock_cli_args)
        utilities.assert_details(
            text=f"Mount {user_gitconfig}",
            expected=os.path.exists(system_gitconfig),
            result=(f"-v {user_gitconfig}:{user_gitconfig}" in args)
        )
        if os.path.exists(user_gitconfig):
            self.assertIn('-v %s:%s' % (user_gitconfig, user_gitconfig), user_args)
