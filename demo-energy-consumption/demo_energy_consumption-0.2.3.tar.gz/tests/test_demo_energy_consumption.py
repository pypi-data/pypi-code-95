#!/usr/bin/env python

"""Tests for `demo_energy_consumption` package."""

import pytest

from click.testing import CliRunner

from demo_energy_consumption import demo_energy_consumption
from demo_energy_consumption import cli


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
    assert 'demo_energy_consumption.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output


def test_getmydata():
    """Test  get_my_data"""

    expected_result = "\n    select \n       \n         $TD_TIMECODE_RANGE as TD_TIMECODE_RANGE\n        ,CAST(BEGIN($TD_TIMECODE_RANGE) AS VARCHAR(32)) as START_PERIOD\n        ,CAST(END($TD_TIMECODE_RANGE) AS VARCHAR(32)) as END_PERIOD\n        \n    -- dimensions\n      ,region,profil,plage_de_puissance_souscrite\n    -- kpis\n      ,sum(total_energie_soutiree_wh) as sum_total_energie_soutiree_wh,avg(courbe_moyenne_num1_num2_Wh) as avg_courbe_moyenne_num1_num2_Wh\n      from  ADLSLSEMEA_ENEDIS.Enedis_conso_hot\n      \n        group by TIME(\n        hours(6)\n        AND region,profil,plage_de_puissance_souscrite)\n        using timecode(horodate)\n      where horodate between DATE '2020-12-01' and DATE '2020-12-31'\n    "
    assert demo_energy_consumption.getmydata(
        table_name='Enedis_conso_hot') == expected_result
