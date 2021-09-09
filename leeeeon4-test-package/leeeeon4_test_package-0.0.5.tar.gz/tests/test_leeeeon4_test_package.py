#!/usr/bin/env python

"""Tests for `leeeeon4_test_package` package."""

import pytest

from click.testing import CliRunner

from leeeeon4_test_package import leeeeon4_test_package
from leeeeon4_test_package import cli


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'leeeeon4_test_package.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output


def test_ingredients(capsys):
    """We use the capsys argument to capture printing to stdout."""
    # The ingredients function prints the results, but returns nothing.
    assert leeeeon4_test_package.ingredients(10) is None

    # Capture the result of the arepas.ingredients() function call.
    captured = capsys.readouterr()

    # If we check captured, we can see that the ingredients have been printed.
    assert "1.0 cups arepa flour" in captured.out
    assert "1.0 cups cheese" in captured.out
    assert "0.25 cups water" in captured.out
