from test.conftest import USE_MOCK

import pytest

import savvihub


@pytest.mark.skipif(USE_MOCK, reason="Does not run if mocking is used.")
class TestKernelResourceSpec:
    def test_read_kernel_resource_spec(self):
        savvihub.read_kernel_resource_spec("v1.cpu-0.mem-1")

    def test_list_kernel_resource_specs(self):
        savvihub.list_kernel_images()
