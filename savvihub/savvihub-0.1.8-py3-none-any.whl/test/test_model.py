from test.conftest import USE_MOCK

import pytest

import savvihub


@pytest.mark.skipif(USE_MOCK, reason="Does not run if mocking is used.")
class TestModel:
    def test_create_model(self):
        # Do not test because requires completed experiment with no errors
        pass

    def test_list_models(self):
        savvihub.list_models()

    def test_read_model(self):
        # Do not test because requires completed experiment with no errors
        pass

    def test_update_model(self):
        # Do not test because requires completed experiment with no errors
        pass

    def test_delete_model(self):
        # Do not test because requires completed experiment with no errors
        pass
