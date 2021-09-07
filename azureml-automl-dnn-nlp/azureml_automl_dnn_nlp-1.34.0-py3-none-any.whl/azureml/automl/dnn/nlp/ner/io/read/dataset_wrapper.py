# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Named entity recognition dataset wrapper class."""

import logging
from typing import List, Optional
import numpy as np

from torch import nn
from torch.utils.data.dataset import Dataset
from transformers import PreTrainedTokenizer

from azureml.automl.dnn.nlp.ner.utils import Split
from azureml.automl.dnn.nlp.common.constants import DataLiterals

logger = logging.getLogger(__name__)


class DatasetWrapper(Dataset):
    """This will be superseded by a framework-agnostic approach soon."""

    def __init__(
            self,
            data,
            tokenizer: PreTrainedTokenizer,
            labels: List[str],
            max_seq_length: Optional[int] = None,
            mode: Split = Split.train
    ):
        """Token classification dataset constructor func."""
        data = data.replace("-DOCSTART- O\n\n", "")
        self.data = data.split("\n\n")

        # handle extra empty line in the end
        if len(self.data) > 1 and self.data[-1] == "":
            del self.data[-1]
        if len(self.data) > 1 and self.data[-1][-1] == "\n":
            self.data[-1] = self.data[-1][:-1]

        self.tokenizer = tokenizer
        self.label_map = {label: i for i, label in enumerate(labels)}
        self.mode = mode
        self.max_seq_length = max_seq_length

    def __len__(self):
        """Token classification dataset len func."""
        return len(self.data)

    def __getitem__(self, idx):
        """Token classification dataset getitem func."""

        tokens = self.data[idx].split("\n")
        if self.mode == Split.train or self.mode == Split.dev or " " in tokens[0]:
            # if training, validating, or if test contains labels, read labels from the dataset
            splits = [item.split(" ") for item in tokens if item not in DataLiterals.NER_IGNORE_TOKENS]
            words = [item[0] for item in splits]
            labels = [item[-1] for item in splits]
        else:
            words = [item for item in tokens if item not in DataLiterals.NER_IGNORE_TOKENS]
            labels = ["O" for item in words]

        tokenized = self.tokenizer(words,
                                   None,
                                   max_length=self.max_seq_length,
                                   padding='max_length',
                                   return_token_type_ids=True,
                                   truncation=True,
                                   is_split_into_words=True)

        # The code below sets label ids for tokens computed above
        # Set padding to nn.CrossEntropyLoss().ignore_index so it isnt used in loss computation
        pad_id = nn.CrossEntropyLoss().ignore_index
        label_ids = np.full((self.max_seq_length), fill_value=pad_id, dtype=np.int32)

        token_idx = 1  # start with index 1 because 0 is a special token
        label_idx = 0
        for label_idx in range(len(words)):

            if token_idx < self.max_seq_length:
                # set label at the starting index of the token
                label_ids[token_idx] = self.label_map[labels[label_idx]]

            # increment token index according to number of tokens generated for the 'word'
            # Note that BERT can create multiple tokens for single word in a language
            token_idx += len(self.tokenizer.tokenize(words[label_idx]))
            # TODO: Remove extra tokenization step if possible ^

        # this should only be added during Split.test once we stop return labels for test split
        tokenized["label_ids"] = [int(item) for item in label_ids]

        return tokenized
