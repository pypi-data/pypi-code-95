import pytest

from propertypro.propertypro import Propertypro


def test_scrape_data() -> None: 
    assert len(Propertypro().scrape_data(100, ["enugu"])) == 105
