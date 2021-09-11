from pbcommon.utils import str_to_date, date_to_str, clean_cme_quote, DATE_FORMAT_STRING
from datetime import datetime

def test_str_to_date():

    dt = datetime(2021,1,1)

    assert date_to_str(dt) == dt.strftime(DATE_FORMAT_STRING)


def test_date_to_str():
    dt = datetime(2021, 1, 1)
    dt_as_str = dt.strftime(DATE_FORMAT_STRING)

    assert str_to_date(dt_as_str) == dt


def test_clean_cme_quote():
    assert clean_cme_quote('1,AB-') == '10'
    assert clean_cme_quote('C,AB-') == 'C0'

