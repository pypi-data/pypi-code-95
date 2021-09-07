#!/usr/bin/env python

"""Tests for `magento_client` package."""

import pytest

from click.testing import CliRunner

from magento_client import magento_client
from magento_client import cli


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

# Todo: fix this to work with client
# def test_client_creation():
#
#     tripletex = tripletex_client.Tripletex(
#         consumer_token="<your_consumer_token>",
#         employee_token="<your_employee_token>",
#     )
#     assert(isinstance(tripletex, tripletex_client.Tripletex))


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'magento_client.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output
