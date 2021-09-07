import pytest
import transformers
import os

from azureml.automl.dnn.nlp.ner.io.read.dataset_wrapper import DatasetWrapper
from azureml.automl.dnn.nlp.ner.utils import Split


@pytest.mark.usefixtures('new_clean_dir')
class TestDatasetWrapper:
    @pytest.mark.parametrize('split', [Split.train, Split.test, Split.dev])
    def test_token_classification_dataset(self, split, get_tokenizer):
        max_seq_length = 20
        mode = split

        with open(os.path.join('ner_data', 'sample_test.txt'), 'r') as f:
            data = f.read()
        test_dataset = DatasetWrapper(
            data=data,
            tokenizer=get_tokenizer,
            labels=["O", "B-MISC", "I-MISC", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC"],
            max_seq_length=max_seq_length,
            mode=mode
        )
        assert len(test_dataset) == 3
        for test_example in test_dataset:
            assert type(test_example) == transformers.tokenization_utils_base.BatchEncoding
            assert len(test_example.input_ids) == max_seq_length
            assert len(test_example.attention_mask) == max_seq_length
            assert len(test_example.token_type_ids) == max_seq_length

            if mode == Split.train or mode == Split.dev:
                assert len(test_example.label_ids) == max_seq_length
            else:
                # Once we stop returning labels for test data, add this assert
                # assert "label_ids" not in test_example
                pass
