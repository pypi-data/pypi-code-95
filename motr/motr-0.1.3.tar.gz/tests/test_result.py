import pytest


@pytest.mark.parametrize("name", ["PASSED", "FAILED", "ABORTED"])
def test_failed(result, name):
    failed = name != "PASSED"
    assert result.Result[name].failed is failed
