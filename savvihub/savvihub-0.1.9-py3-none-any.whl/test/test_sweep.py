from test.conftest import USE_MOCK

import pytest

import savvihub
from savvihub.util.constant import (
    PROJECT_TYPE_CLI_DRIVEN,
    SWEEP_ALGORITHM_TYPE_RANDOM,
    SWEEP_OBJECTIVE_TYPE_MAXIMIZE,
)


@pytest.mark.skipif(USE_MOCK, reason="Does not run if mocking is used.")
class TestSweep:
    @pytest.mark.order(index=1)
    def test_create_sweep(self):
        # Requires sweep suggestion server
        # pytest.sweep = savvihub.create_sweep(
        #     objective_type=SWEEP_OBJECTIVE_TYPE_MAXIMIZE,
        #     objective_goal=0.99,
        #     objective_metric="val_accuracy",
        #     max_experiment_count=2,
        #     parallel_experiment_count=1,
        #     max_failed_experiment_count=1,
        #     algorithm=SWEEP_ALGORITHM_TYPE_RANDOM,
        #     parameters=[
        #         {"name": "a", "type": "int", "range": {"list": ["1", "2", "3"]}}
        #     ],
        #     cluster_name="local",
        #     start_command="echo 'Hello world!'",
        #     kernel_resource_spec_name="v1.cpu-0.mem-1",
        #     kernel_image_url="savvihub/kernels:py36.full-cpu",
        #     local_project_url="",
        # )
        pass

    def test_read_sweep(self):
        # Requires sweep suggestion server
        pass

    def test_list_sweeps(self):
        savvihub.list_sweeps()

    def test_terminate_sweep(self):
        # Requires sweep suggestion server
        pass

    def test_list_sweep_logs(self):
        # Requires sweep suggestion server
        pass
