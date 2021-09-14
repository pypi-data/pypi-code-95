import unittest
import pytest
import tempfile
import shutil
from bmlx.context import BmlxContext
from bmlx.metadata.metadata import Metadata
from bmlx.flow import Artifact, Pipeline
from bmlx.execution.launcher import Launcher, DriverArgs
from bmlx_components.importer_node.component import ImporterNode
from unittest.mock import Mock
from bmlx.config import Configuration


class MockArtifact(Artifact):
    TYPE_NAME = "test_mock_artifact"


class KubeflowStoreTests(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.context = BmlxContext()
        self.context.local_mode = True
        self.context._store = Metadata(
            local_mode=True, local_storage_path=self.test_dir
        )
        self.importer = ImporterNode(
            source_uri="hdfs://mock",
            instance_name="test_importer",
            artifact_type=MockArtifact,
            import_checker="check_nothing",
        )

        self.pipeline = Pipeline(
            name="test-pipeline", components=[self.importer]
        )

        self.pipeline_execution = self.context.metadata.get_or_create_pipeline_execution(
            pipeline=self.pipeline,
        )
        self.artifact_base = tempfile.mkdtemp()
        # mock artifact storage base
        self.context.project = Mock()
        self.context.project.configure_mock(
            artifact_storage_base=self.artifact_base,
            configs=Configuration(default={}),
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def testNormal(self):
        launcher = Launcher(
            context=self.context,
            component=self.importer,
            pipeline=self.pipeline,
            driver_args=DriverArgs(
                pipeline_execution=self.pipeline_execution,
                prepare_output_uri=False,  # essential for testing
            ),
        )

        launcher.launch()

        component_executions = self.context.metadata.store.get_component_executions_of_pipeline(
            pipeline_execution=self.pipeline_execution
        )

        self.assertEqual(len(component_executions), 1)

        (
            input_artifacts,
            output_artifacts,
        ) = self.context.metadata.store.get_component_executions_artifacts(
            component_executions=component_executions
        )
        self.assertEqual(len(input_artifacts), 0)
        self.assertEqual(len(output_artifacts), 1, output_artifacts)
        self.assertEqual(output_artifacts[0].uri, "hdfs://mock")

    def testImportFail_UriNotExist(self):
        importer = ImporterNode(
            source_uri="/mock-test",
            instance_name="test_importer",
            artifact_type=MockArtifact,
            import_checker="check_uri_exist",
        )
        launcher = Launcher(
            context=self.context,
            component=importer,
            pipeline=self.pipeline,
            driver_args=DriverArgs(
                pipeline_execution=self.pipeline_execution,
                prepare_output_uri=False,  # essential for testing
            ),
        )
        # will raise RuntimeError because uri does not exist
        with pytest.raises(RuntimeError) as excinfo:
            launcher.launch()

        assert "check artifact /mock-test failed" in str(excinfo.value)
