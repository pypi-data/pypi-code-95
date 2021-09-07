#!/usr/bin/env python

"""Tests for `nlon_py` package."""


import unittest
from click.testing import CliRunner

from nlon_py import nlon_py
from nlon_py import cli


class TestNlon_py(unittest.TestCase):
    """Tests for `nlon_py` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'nlon_py.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
