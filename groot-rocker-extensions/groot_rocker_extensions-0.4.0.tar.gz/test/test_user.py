#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# License: BSD
#   https://raw.githubusercontent.com/stonier/groot_rocker_extensions/devel/LICENSE
#

##############################################################################
# Imports
##############################################################################

import getpass
import os
import pathlib
import pwd

from . import utilities

##############################################################################
# Tests
##############################################################################


class User(utilities.ExtensionTestCase):

    def test_environment_queries(self):
        env_subs = self.extension.get_environment_subs()
        utilities.assert_details(
            text="Environment::gid",
            expected=os.getgid(),
            result=env_subs['gid']
        )
        self.assertEqual(env_subs['gid'], os.getgid())
        utilities.assert_details(
            text="Environment::uid",
            expected=os.getuid(),
            result=env_subs['uid']
        )
        self.assertEqual(env_subs['uid'], os.getuid())
        utilities.assert_details(
            text="Environment::name",
            expected=getpass.getuser(),
            result=env_subs['name']
        )
        self.assertEqual(env_subs['name'],  getpass.getuser())
        utilities.assert_details(
            text="Environment::dir",
            expected=str(pathlib.Path.home()),
            result=env_subs['dir']
        )
        self.assertEqual(env_subs['dir'],  str(pathlib.Path.home()))
        utilities.assert_details(
            text="Environment::gecos",
            expected=pwd.getpwuid(os.getuid()).pw_gecos,
            result=env_subs['gecos']
        )
        self.assertEqual(env_subs['gecos'],  pwd.getpwuid(os.getuid()).pw_gecos)
        utilities.assert_details(
            text="Environment::shell",
            expected=pwd.getpwuid(os.getuid()).pw_shell,
            result=env_subs['shell']
        )
        self.assertEqual(env_subs['shell'],  pwd.getpwuid(os.getuid()).pw_shell)

        mock_cliargs = {}
        snippet = self.extension.get_snippet(mock_cliargs).splitlines()

        uid_line = [l for l in snippet if '--uid' in l][0]
        self.assertTrue(str(os.getuid()) in uid_line)

        self.assertEqual(self.extension.get_preamble(mock_cliargs), '')
        self.assertEqual(self.extension.get_docker_args(mock_cliargs), '')

        self.assertTrue('mkhomedir_helper' in self.extension.get_snippet(mock_cliargs))
        home_active_cliargs = mock_cliargs
        home_active_cliargs['home'] = True
        self.assertFalse('mkhomedir_helper' in self.extension.get_snippet(home_active_cliargs))

