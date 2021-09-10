import dad_tool
import pytest


def test_random_address():
    address = dad_tool.random_address('US_UT')

    assert address['state'] == 'UT'


def test_list_addresses():
    addresses = dad_tool.list_addresses('US_UT')

    assert len(addresses) == 100
    assert addresses[0]['state'] == 'UT'


def test_bad_data():
    with pytest.raises(KeyError) as error:
        _ = dad_tool.random_address('BAD_DATA')

    assert '\'BAD_DATA\'' == str(error.value)


def test_list_iso_country_codes():
    with pytest.raises(NotImplementedError):
        _ = dad_tool.list_iso_country_codes()
