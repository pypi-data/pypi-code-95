import numpy as np
import pandas as pd
import pytest
from unittest.mock import MagicMock, patch

from azureml.automl.dnn.nlp.classification.multiclass import runner

from ...mocks import aml_dataset_mock, MockRun, multiclass_trainer_mock


@pytest.mark.usefixtures('MulticlassDatasetTester')
@pytest.mark.usefixtures('MulticlassValDatasetTester')
@pytest.mark.parametrize('multiple_text_column', [True, False])
@pytest.mark.parametrize('include_label_col', [True])
class TestMulticlassRunner:
    """Tests for Multiclass runner."""

    @patch("azureml.automl.dnn.nlp.classification.multiclass.trainer.Trainer")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.trainer.AutoModelForSequenceClassification")
    @patch("azureml.core.Dataset.get_by_id")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.parse_settings")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.prepare_run_properties")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.save_conda_yml")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.save_script")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.prepare_post_run_properties")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.save_model_wrapper")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.Run")
    def test_runner_test(
            self,
            save_model_mock,
            run_mock,
            prepare_post_properties_mock,
            save_script_mock,
            conda_yml_mock,
            prepare_properties_mock,
            parse_settings_mock,
            get_by_id_mock,
            model_mock,
            trainer_mock,
            MulticlassDatasetTester,
            MulticlassValDatasetTester
    ):
        # run mock
        mock_run = MockRun()
        run_mock.get_context.return_value = mock_run

        # settings mock
        automl_settings = {
            "task_type": "text-classification",
            "primary_metric": "accuracy",
            "dataset_id": "mock_dataset_id",
            "validation_dataset_id": "mock_validation_dataset_id",
            "label_column_name": "labels_col"
        }
        mock_settings = MagicMock()
        mock_settings.dataset_id = "mock_dataset_id"
        mock_settings.validation_dataset_id = "mock_validation_dataset_id"
        mock_settings.label_column_name = "labels_col"
        parse_settings_mock.return_value = mock_settings

        # dataset get_by_id mock
        train_df = MulticlassDatasetTester.get_data().copy()
        val_df = MulticlassValDatasetTester.get_data().copy()
        concat_df = pd.concat([train_df, val_df], ignore_index=True)
        mock_aml_dataset = aml_dataset_mock(concat_df)
        get_by_id_mock.return_value = mock_aml_dataset

        # model mock
        model = MagicMock()
        model.from_pretrained.return_value = MagicMock()
        model_mock.return_value = model

        # trainer mock
        mock_trainer = multiclass_trainer_mock(len(concat_df))
        trainer_mock.return_value = mock_trainer

        # Test runner
        runner.run(automl_settings)

        # Asserts
        mock_trainer.train.assert_called_once()
        mock_trainer.save_model.assert_called_once()
        mock_trainer.save_state.assert_called_once()
        mock_trainer.save_metrics.assert_called_once()

    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.parse_settings")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.Run")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.dataloader")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.TextClassificationTrainer")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.prepare_post_run_properties")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.save_conda_yml")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.save_script")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner.save_model_wrapper")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.runner._get_language_code")
    def test_runner_language_continuity(self, language_mock, save_model_mock, score_mock, conda_mock, post_run_mock,
                                        trainer_mock, dataload_mock, run_mock, parse_mock):
        run_mock.get_context.return_value = MagicMock()
        run_mock.experiment.workspace = "some_workspace"
        parse_mock.return_value = MagicMock()
        parse_mock.return_value.validation_dataset_id = None

        language_mock.return_value = 'some_language'

        dataload_mock.multiclass_dataset_loader.return_value =\
            "train_set", MagicMock(), np.array([0, 1, 2, 3, 4]), np.array([0, 1, 2, 3]), np.array([1, 4, 3, 1, 2])

        mock_trainer = multiclass_trainer_mock(5)
        trainer_mock.return_value = mock_trainer
        score_mock.return_value = MagicMock()

        runner.run("ignored_input")
        assert dataload_mock.multiclass_dataset_loader.call_args[0][4] == "some_language"
        assert trainer_mock.call_args[0][1] == "some_language"
