import pytest

from sim_metrics import elmwise


def test_ae():
    assert pytest.approx(elmwise.ae(3.4, 3.4), 0, abs=1e-15)
    assert pytest.approx(elmwise.ae(3.4, 4.4), 1.0, abs=1e-15)
    assert pytest.approx(elmwise.ae(9, 11), 2, abs=1e-15)


def test_mae():
    assert pytest.approx(elmwise.mae(range(0, 11), range(1, 12)), 1, abs=1e-15)
    assert pytest.approx(elmwise.mae([0, .5, 1, 1.5, 2], [0, .5, 1, 1.5, 2]), 0, abs=1e-15)
    assert pytest.approx(elmwise.mae(range(1, 5), [1, 2, 3, 5]), 0.25, abs=1e-15)


def test_mse():
    assert pytest.approx(elmwise.mse(range(0, 11), range(1, 12)), 1, abs=1e-15)
    assert pytest.approx(elmwise.mse([0, .5, 1, 1.5, 2], [0, .5, 1, 1.5, 2]), 0, abs=1e-15)
    assert pytest.approx(elmwise.mse(range(1, 5), [1, 2, 3, 6]), 1.0, abs=1e-15)


def test_rmse():
    assert pytest.approx(elmwise.rmse(range(0, 11), range(1, 12)), 1, abs=1e-15)
    assert pytest.approx(elmwise.rmse([0, .5, 1, 1.5, 2], [0, .5, 1, 1.5, 2]), 0, abs=1e-15)
    assert pytest.approx(elmwise.rmse(range(1, 5), [1, 2, 3, 5]), 0.5, abs=1e-15)


def test_rrmse():
    assert pytest.approx(elmwise.rrmse(range(0, 11), range(1, 12)), 0.2, abs=1e-15)
    assert pytest.approx(elmwise.rrmse([0, .5, 1, 1.5, 2], [0, .5, 1, 1.5, 2]), 0, abs=1e-15)
    assert pytest.approx(elmwise.rrmse(range(1, 5), [1, 2, 3, 5]), 0.1, abs=1e-15)


def test_se():
    assert pytest.approx(elmwise.se(3.4, 3.4), 0, abs=1e-15)
    assert pytest.approx(elmwise.se(3.4, 4.4), 1.0, abs=1e-15)
    assert pytest.approx(elmwise.se(9, 11), 4, abs=1e-15)
