import tempfile
from pathlib import Path
from typing import List, Mapping, Optional

from microcosm.loaders import load_each, load_from_dict

from microcosm_sagemaker.app_hooks import create_evaluate_app
from microcosm_sagemaker.bundle import Bundle
from microcosm_sagemaker.commands import train
from microcosm_sagemaker.testing.bundle_prediction_check import BundlePredictionCheck
from microcosm_sagemaker.testing.bytes_extractor import ExtractorMatcherPair
from microcosm_sagemaker.testing.cli_test_case import CliTestCase
from microcosm_sagemaker.testing.directory_comparison import directory_comparison


class TrainCliTestCase(CliTestCase):
    """
    Helper base class for writing tests of the train cli.

    """
    input_data_path: Path
    gold_output_artifact_path: Optional[Path] = None
    output_artifact_matchers: Mapping[Path, ExtractorMatcherPair]
    bundle_prediction_checks: Optional[List[BundlePredictionCheck]] = None

    @property
    def extra_evaluate_config(self) -> dict:
        """
        Derived classes can override this to provide extra config to the
        evalute create_app function when evaluating the active bundle.

        """
        return {}

    def test_train(self) -> None:
        """
        Runs the `train` command on the given `input_data_path` and then
        recursively checks the contents of the output artifact against the
        expected contents in `gold_output_artifact_path`.  It is also possible
        to leave certain files out of the gold dir, and instead specify a
        matcher that should be used for the contents of the given file instead.

        """
        with tempfile.TemporaryDirectory() as output_artifact_path:
            self.run_and_check(
                command_name="train",
                command=train.main,
                args=[
                    "--input-data",
                    str(self.input_data_path),
                    "--output-artifact",
                    output_artifact_path,
                    "--testing",
                ],
            )

            self.check_output_artifact(Path(output_artifact_path))

            self.graph = create_evaluate_app(
                extra_loader=load_each(
                    load_from_dict(
                        root_input_artifact_path=output_artifact_path,
                    ),
                    load_from_dict(self.extra_evaluate_config),
                ),
                testing=True,
            )

            self.check_bundle(self.graph.active_bundle)

    def check_output_artifact(self, output_artifact_path: Path):
        """
        Checks the training output artifact.  Can be overridden to perform
        customized checks.

        """
        if self.gold_output_artifact_path:
            directory_comparison(
                gold_dir=self.gold_output_artifact_path,
                actual_dir=output_artifact_path,
                matchers=self.output_artifact_matchers,
            )

    def check_bundle(self, bundle: Bundle):
        """
        Checks the active bundle after loading trained artifact.  Derived
        classes can override this to perform custom bundle checks.

        """
        if self.bundle_prediction_checks:
            for bundle_prediction_check in self.bundle_prediction_checks:
                bundle_prediction_check.check_bundle(bundle)
