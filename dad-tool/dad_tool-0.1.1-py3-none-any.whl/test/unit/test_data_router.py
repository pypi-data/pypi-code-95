import dad_python
import pytest


def test_random_address():
    address = dad_python.random_address('US_UT')

    assert address['state'] == 'UT'


def test_list_addresses():
    addresses = dad_python.list_addresses('US_UT')

    assert len(addresses) == 100
    assert addresses[0]['state'] == 'UT'


def test_bad_data():
    with pytest.raises(KeyError) as error:
        _ = dad_python.random_address('BAD_DATA')

    assert '\'BAD_DATA\'' == str(error.value)


def test_list_iso_country_codes():
    with pytest.raises(NotImplementedError):
        _ = dad_python.list_iso_country_codes()
