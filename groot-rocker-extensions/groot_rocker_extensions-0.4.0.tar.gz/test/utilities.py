#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# License: BSD
#   https://raw.githubusercontent.com/stonier/groot_rocker_extensions/devel/LICENSE
#

##############################################################################
# Imports
##############################################################################

import argparse
import em
import re
import unittest

import groot_rocker
import groot_rocker.console as console

##############################################################################
# Helper Methods
##############################################################################


def assert_details(text, expected, result):
    print(console.green + text +
          "." * (40 - len(text)) +
          console.cyan + "{}".format(expected) +
          console.yellow + " [{}]".format(result) +
          console.reset)


##############################################################################
# Imports
##############################################################################


class ExtensionTestCase(unittest.TestCase):

    def setUp(self):
        """
        Children should implement their own setup() method and:

         * set self.extension_name appropriately
         * call this (the parent setup() method)
        """
        self.extension_name = re.sub(r'(?<!^)(?=[A-Z])', '_', self.__class__.__name__).lower()
        # Work around interference between empy Interpreter
        # stdout proxy and test runner. empy installs a proxy on stdout
        # to be able to capture the information.
        # And the test runner creates a new stdout object for each test.
        # This breaks empy as it assumes that the proxy has persistent
        # between instances of the Interpreter class
        # empy will error with the exception
        # "em.Error: interpreter stdout proxy lost"
        em.Interpreter._wasProxyInstalled = False
        # Ensure that a user of this class has set self.extension_name
        try:
            hasattr(self, "extension_name")
        except AttributeError:
            raise AssertionError("Children must provide a value for self.extension_name (e.g. 'user')")
        assert isinstance(self.extension_name, str), "self.extension_name must be a str type"
        self.extensions = groot_rocker.core.list_plugins()
        self.extension_class = self.extensions[self.extension_name]
        self.extension = self.extension_class()
        print("\n")  # clearly delineates between test methods

    def test_extension_name(self):
        assert_details(
            text="Extension Name",
            expected=self.extension_name,
            result=self.extension.get_name()
        )
        self.assertEqual(self.extension.get_name(), self.extension_name)

    def test_load_parser_correctly(self):
        """
        A helper function to test that the plugins at least
        register an option for their own name.
        """
        parser = argparse.ArgumentParser(description='test_parser')
        self.extension.register_arguments(parser)
        argument_name = groot_rocker.extensions.name_to_argument(self.extension.get_name())
        found_string = False
        for action in parser._actions:
            option_strings = getattr(action, 'option_strings', [])
            if argument_name in option_strings:
                found_string = True
                break
        assert_details(
            text="Extension Name as Argparse Arg",
            expected=True,
            result=found_string
        )
        self.assertTrue(found_string)

