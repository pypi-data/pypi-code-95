# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
#
# For PyTorchDatasetWrapper:
#
# MIT License
#
# Copyright (c) 2020 Abhishek Kumar Mishra
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""PyTorchDatasetWrapper class for text tasks"""

import logging
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset as PyTorchDataset
from transformers import BertTokenizer, AutoTokenizer
from typing import Union

from azureml.automl.dnn.nlp.common.constants import ModelNames
from azureml.automl.dnn.nlp.classification.common.constants import (
    DatasetLiterals,
    MultiClassParameters,
    MultiLabelParameters
)
from azureml.automl.dnn.nlp.common._model_selector import get_model_from_language

logger = logging.getLogger(__name__)


class PyTorchDatasetWrapper(PyTorchDataset):
    """Class for obtaining dataset to be passed into model."""

    def __init__(self, dataframe, label_column_name=None, vectorizer=None):
        """ Init function definition

        :param dataframe: pd.DataFrame holding data to be passed
        :param label_column_name: name/title of the label column
        :param vectorizer: Optional fitted CountVectorizer to transform the
                           Multilabel labels column to one-hot encoding
        """
        self.tokenizer = BertTokenizer.from_pretrained(ModelNames.BERT_BASE_UNCASED)
        self.data = dataframe
        self.targets = None
        if label_column_name is not None:
            self.targets = self.data[label_column_name]
        self.max_len = MultiLabelParameters.MAX_LEN
        self.label_column_name = label_column_name
        self.vectorizer = vectorizer

    def __len__(self):
        """Len function definition."""
        return len(self.data)

    def _concat_text_columns(self, index):
        all_texts = [self.data[column][index] for column in self.data.columns
                     if self.label_column_name is None or self.label_column_name != column]
        comment_text = " ".join(all_texts)
        return comment_text

    def __getitem__(self, index):
        """Getitem function definition."""
        comment_text = self._concat_text_columns(index)
        inputs = self.tokenizer.encode_plus(
            comment_text,
            None,
            add_special_tokens=True,
            max_length=self.max_len,
            padding='max_length',
            return_token_type_ids=True,
            truncation=True
        )
        ids = inputs['input_ids']
        mask = inputs['attention_mask']
        token_type_ids = inputs["token_type_ids"]

        if self.targets is None:
            return {
                'ids': torch.tensor(ids, dtype=torch.long),
                'mask': torch.tensor(mask, dtype=torch.long),
                'token_type_ids': torch.tensor(token_type_ids, dtype=torch.long),
            }

        else:
            label_col = np.array([self.targets[index]])
            count_array = self.vectorizer.transform(label_col)
            labels = count_array.toarray().astype(float)[0]

            return {
                'ids': torch.tensor(ids, dtype=torch.long),
                'mask': torch.tensor(mask, dtype=torch.long),
                'token_type_ids': torch.tensor(token_type_ids, dtype=torch.long),
                'targets': torch.tensor(labels, dtype=torch.float)
            }


class PyTorchMulticlassDatasetWrapper(PyTorchDataset):
    """
    Class for obtaining dataset to be passed into model for multi-class classification.
    This is based on the datasets.Dataset package from HuggingFace.
    """

    def __init__(self, dataframe: pd.DataFrame, train_label_list: np.ndarray,
                 dataset_language: str,
                 label_column_name: Union[str, None] = None):
        """ Init function definition

        :param dataframe: pd.DataFrame holding data to be passed
        :param train_label_list: list of labels from training data
        :param dataset_language: language code of dataset
        :param label_column_name: name/title of the label column
        """
        self.label_to_id = {v: i for i, v in enumerate(train_label_list)}
        model_name, _ = get_model_from_language(dataset_language)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
        self.data = dataframe
        self.label_column_name = label_column_name

        # Padding strategy
        self.padding = False
        if MultiClassParameters.PAD_TO_MAX_LENGTH:
            self.padding = MultiClassParameters.MAX_LEN_PADDING

        self.max_seq_length = min(MultiClassParameters.MAX_SEQ_LENGTH, self.tokenizer.model_max_length)

    def __len__(self):
        """Len function definition."""
        return len(self.data)

    def _concat_text_columns(self, index):
        """Concatenate all text columns"""
        all_texts = [self.data[column][index] for column in self.data.columns
                     if self.label_column_name is None or self.label_column_name != column]
        comment_text = ". ".join(map(str, all_texts))
        return comment_text

    def __getitem__(self, index):
        """Getitem function definition."""
        sample = self._concat_text_columns(index)
        tokenized = self.tokenizer(sample, padding=self.padding, max_length=self.max_seq_length, truncation=True)

        if self.label_column_name is not None and self.label_to_id is not None and \
           self.label_column_name in self.data.columns:
            label = self.data[self.label_column_name][index]
            tokenized[DatasetLiterals.LABEL_COLUMN] = self.label_to_id[label]

        return tokenized
