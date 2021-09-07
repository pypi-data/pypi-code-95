import numpy as np
import pandas as pd
import pytest
import unittest
from unittest.mock import MagicMock, patch
from azureml.automl.dnn.nlp.classification.common.constants import DatasetLiterals
from azureml.automl.dnn.nlp.classification.io.read.dataloader import (
    multiclass_dataset_loader
)
from azureml.automl.dnn.nlp.classification.io.read.pytorch_dataset_wrapper import PyTorchMulticlassDatasetWrapper
from ...mocks import aml_dataset_mock
try:
    import torch
    has_torch = True
except ImportError:
    has_torch = False


@pytest.mark.usefixtures('MulticlassDatasetTester')
class TestTextClassificationDataLoadTests:
    """Tests for Text Classification data loader."""
    @pytest.mark.parametrize('multiple_text_column', [True, False])
    @pytest.mark.parametrize('include_label_col', [True, False])
    def test_concat_text_and_preserve_label(self, MulticlassDatasetTester, include_label_col):
        input_df = MulticlassDatasetTester.get_data().copy()
        multiple_cols = MulticlassDatasetTester.multiple_text_column
        label_column_name = "labels_col"

        if include_label_col:
            label_list = pd.unique(input_df[label_column_name])
            dataset = PyTorchMulticlassDatasetWrapper(input_df, label_list, 'eng', label_column_name)
            len(dataset[0]) == 4
        else:
            label_list = ["train_label_1", "train_label_2"]
            dataset = PyTorchMulticlassDatasetWrapper(input_df, label_list, 'eng')
            len(dataset[0]) == 3

        input_ids = [item for item in dataset[0][DatasetLiterals.INPUT_IDS] if item != 0]
        if multiple_cols:
            # col 2, row 1 has 5 tokens (see conftest), and col 1, row 1 has 10
            len(input_ids) == 15
        else:
            # col 1, row 1 has 10 tokens (see conftest)
            len(input_ids) == 10

    @unittest.skipIf(not has_torch, "torch not installed")
    @pytest.mark.parametrize('multiple_text_column', [True, False])
    @pytest.mark.parametrize('include_label_col', [True])
    @patch("azureml.automl.dnn.nlp.classification.io.read.pytorch_dataset_wrapper.AutoTokenizer")
    @patch("azureml.automl.dnn.nlp.classification.io.read.pytorch_dataset_wrapper.get_model_from_language")
    def test_pytorch_multiclass_dataset_wrapper(self, language_mock,
                                                tokenizer_mock, MulticlassDatasetTester, multiple_text_column):
        input_df = MulticlassDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        label_list = pd.unique(input_df[label_column_name])
        tokenizer_mock.from_pretrained.return_value.model_max_length = 256
        language_mock.return_value = ('some_model_name', 'some_path_name')
        # Will handle None Type values
        row_num = 4
        input_df['text_first'][row_num] = None
        output_set = PyTorchMulticlassDatasetWrapper(input_df, label_list,
                                                     'eng', label_column_name)
        # To check the addition of a period between the concatenated strings.
        # input_df's text columns on the 4th row don't have any period before concatenation.
        if multiple_text_column:
            assert "." in output_set._concat_text_columns(row_num)
        assert type(output_set) == PyTorchMulticlassDatasetWrapper
        assert len(output_set) == 5
        assert tokenizer_mock.from_pretrained.call_args[0][0] == "some_model_name"
        for i in range(len(output_set)):
            training_keys = set([DatasetLiterals.LABEL_COLUMN, DatasetLiterals.INPUT_IDS,
                                 DatasetLiterals.TOKEN_TYPE_IDS, DatasetLiterals.ATTENTION_MASK])
            assert all([item in training_keys for item in output_set[i].keys()])

            assert all([type(item) == torch.Tensor for item in output_set[i].values()])

    @pytest.mark.parametrize('multiple_text_column', [True, False])
    @pytest.mark.parametrize('include_label_col', [True])
    @patch("azureml.core.Dataset.get_by_id")
    def test_multiclass_dataset_loader(self, get_by_id_mock, MulticlassDatasetTester):
        input_df = MulticlassDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        mock_aml_dataset = aml_dataset_mock(input_df.copy())
        get_by_id_mock.return_value = mock_aml_dataset
        dataset_id = "mock_id"
        validation_dataset_id = "mock_validation_id"
        aml_workspace_mock = MagicMock()
        training_set, validation_set, label_list, _, y_val = multiclass_dataset_loader(
            dataset_id, validation_dataset_id, label_column_name, aml_workspace_mock, dataset_language='eng')
        assert all(np.array(input_df[label_column_name]) == y_val)
        # The returned label_list is sorted, although the original labels weren't
        input_label_list = input_df[label_column_name].unique()
        assert any(label_list != input_label_list)
        input_label_list.sort()
        assert all(label_list == input_label_list)
        for output_set in [training_set, validation_set]:
            assert type(output_set) == PyTorchMulticlassDatasetWrapper
            assert len(output_set) == 5
        for i in range(len(training_set)):
            training_keys = set([DatasetLiterals.LABEL_COLUMN, DatasetLiterals.INPUT_IDS,
                                 DatasetLiterals.TOKEN_TYPE_IDS, DatasetLiterals.ATTENTION_MASK])
            assert all([item in training_keys for item in training_set[i].keys()])
        for i in range(len(validation_set)):
            validation_keys = set([DatasetLiterals.INPUT_IDS,
                                   DatasetLiterals.TOKEN_TYPE_IDS, DatasetLiterals.ATTENTION_MASK])
            assert all([item in validation_keys for item in validation_set[i].keys()])
