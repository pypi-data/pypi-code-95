from datetime import datetime
from test.conftest import USE_MOCK

import pytest

import savvihub
from openapi_client.models import (
    InfluxdbExperimentPlotFile,
    InfluxdbExperimentPlotMetric,
)
from savvihub.util.constant import VESSL_PLOTS_FILETYPE_IMAGE


@pytest.mark.skipif(USE_MOCK, reason="Does not run if mocking is used.")
class TestExperiment:
    @pytest.mark.order(index=1)
    def test_create_experiment(self):
        # Use pytest.experiment instead of self.experiment because self gets reset
        # after each test
        pytest.experiment = savvihub.create_experiment(
            cluster_name="aws-uw2-dev",  # TODO: change when CI server is relocated
            start_command="echo 'Hello world!'",
            kernel_resource_spec_name="v1.cpu-0.mem-1",
            kernel_image_url="savvihub/kernels:py36.full-cpu",
            message="test message",
            termination_protection=False,
            env_vars=[("VAR", "value")],
            local_project_url="",
        )

    def test_read_experiment(self):
        savvihub.read_experiment(pytest.experiment.name)

    def test_read_experiment_by_id(self):
        savvihub.read_experiment_by_id(pytest.experiment.id)

    def test_list_experiments(self):
        savvihub.list_experiments()

    def test_list_experiment_logs(self):
        savvihub.list_experiment_logs(pytest.experiment.name)

    def test_list_experiment_output_files(self):
        savvihub.list_experiment_output_files(pytest.experiment.name)

    def test_download_experiment_output_files(self):
        savvihub.download_experiment_output_files(pytest.experiment.name)

    def test_update_experiment_plots_files(self):
        file = InfluxdbExperimentPlotFile(
            step=None,
            path="test/fixture/file1.txt",
            caption="test-caption",
            timestamp=datetime.utcnow().timestamp(),
        )
        savvihub.update_experiment_plots_files(
            pytest.experiment.id, [file], VESSL_PLOTS_FILETYPE_IMAGE
        )

    def test_update_experiment_plots_metrics(self):
        metric = InfluxdbExperimentPlotMetric(
            step=1,
            timestamp=datetime.utcnow().timestamp(),
            value=1.0,
        )
        savvihub.update_experiment_plots_metrics(
            pytest.experiment.id, {"val_accuracy": [metric]}
        )
