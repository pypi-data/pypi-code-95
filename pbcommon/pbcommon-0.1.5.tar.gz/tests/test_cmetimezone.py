from pbcommon.cmetimezone import cme_now


def test_cme_now():
    assert cme_now().tzinfo.zone == 'US/Central'


def test_cme_now_with_offset_days():
    assert cme_now(1).tzinfo.zone == 'US/Central'
    assert cme_now(1) < cme_now()