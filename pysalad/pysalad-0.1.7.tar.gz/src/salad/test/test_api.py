from .. import api


def test_trim_whitespace():
    assert api.trim_whitespace("\r\ntest\n\r") == "test"
    assert api.trim_whitespace(None) is None
