from test.conftest import USE_MOCK

import pytest

import savvihub


@pytest.mark.skipif(USE_MOCK, reason="Does not run if mocking is used.")
class TestKernelCluster:
    def test_read_cluster(self):
        savvihub.read_cluster("aws-uw2-dev")  # TODO: change when CI server is relocated

    def test_list_clusters(self):
        savvihub.list_clusters()

    def test_delete_cluster(self):
        # Do not test delete cluster because only one cluster exists.
        pass

    def test_rename_cluster(self):
        # Only applies to custom clusters
        pass

    def test_list_cluster_nodes(self):
        # Only applies to custom clusters
        pass
